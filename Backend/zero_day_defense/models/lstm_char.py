from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset


class CharDataset(Dataset):
    def __init__(self, texts: List[str], stoi: dict, max_len: int):
        self.texts = texts
        self.stoi = stoi
        self.max_len = max_len

    def __len__(self) -> int:
        return len(self.texts)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        s = (self.texts[idx] or "")[: self.max_len]
        # next-char prediction: input is chars[0:-1], target is chars[1:]
        ids = [self.stoi.get(ch, self.stoi["<unk>"]) for ch in s]
        if len(ids) < 2:
            ids = ids + [self.stoi["<pad>"]] * (2 - len(ids))
        x = ids[:-1]
        y = ids[1:]
        # pad to max_len-1
        pad_len = (self.max_len - 1) - len(x)
        if pad_len > 0:
            x = x + [self.stoi["<pad>"]] * pad_len
            y = y + [self.stoi["<pad>"]] * pad_len
        else:
            x = x[: self.max_len - 1]
            y = y[: self.max_len - 1]
        return torch.tensor(x, dtype=torch.long), torch.tensor(y, dtype=torch.long)


class CharLSTM(nn.Module):
    def __init__(self, vocab_size: int, embedding_dim: int, hidden_dim: int):
        super().__init__()
        self.emb = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
        self.lstm = nn.LSTM(embedding_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, vocab_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        e = self.emb(x)
        h, _ = self.lstm(e)
        return self.fc(h)


@dataclass
class LSTMCharModel:
    stoi: dict
    itos: list
    net: CharLSTM
    max_len: int

    def score(self, texts: List[str], device: str = "cpu", batch_size: int = 256) -> np.ndarray:
        self.net.eval()
        ds = CharDataset(texts, self.stoi, self.max_len)
        dl = DataLoader(ds, batch_size=batch_size, shuffle=False)
        losses: List[float] = []
        loss_fn = nn.CrossEntropyLoss(ignore_index=self.stoi["<pad>"], reduction="none")
        with torch.no_grad():
            for xb, yb in dl:
                xb = xb.to(device)
                yb = yb.to(device)
                logits = self.net(xb)  # [B,T,V]
                B, T, V = logits.shape
                per_tok = loss_fn(logits.reshape(B * T, V), yb.reshape(B * T)).reshape(B, T)
                mask = (yb != self.stoi["<pad>"]).float()
                seq_loss = (per_tok * mask).sum(dim=1) / torch.clamp(mask.sum(dim=1), min=1.0)
                losses.extend(seq_loss.detach().cpu().numpy().tolist())
        arr = np.asarray(losses, dtype=np.float32)
        # convert to anomaly score in [0,1] using robust z then squashing
        med = float(np.median(arr))
        mad = float(np.median(np.abs(arr - med)) + 1e-6)
        z = (arr - med) / (1.4826 * mad)
        z = np.clip(z, 0, 50)
        return 1.0 - np.exp(-z)


def build_vocab(texts: List[str], max_vocab: int = 128) -> Tuple[dict, list]:
    # Character vocabulary; keep common ASCII + whatever appears.
    freq = {}
    for s in texts:
        for ch in (s or ""):
            freq[ch] = freq.get(ch, 0) + 1
    # special tokens
    itos = ["<pad>", "<unk>"]
    # pick top chars
    chars = sorted(freq.items(), key=lambda kv: kv[1], reverse=True)
    for ch, _ in chars:
        if ch in itos:
            continue
        itos.append(ch)
        if len(itos) >= max_vocab:
            break
    stoi = {ch: i for i, ch in enumerate(itos)}
    return stoi, itos


def train_lstm_char(texts_train: List[str], cfg: Dict, device: str = "cpu") -> LSTMCharModel:
    max_len = int(cfg["lstm"]["max_len"])
    stoi, itos = build_vocab(texts_train)
    ds = CharDataset(texts_train, stoi, max_len)
    dl = DataLoader(ds, batch_size=int(cfg["lstm"]["batch_size"]), shuffle=True)

    net = CharLSTM(
        vocab_size=len(itos),
        embedding_dim=int(cfg["lstm"]["embedding_dim"]),
        hidden_dim=int(cfg["lstm"]["hidden_dim"]),
    ).to(device)
    opt = torch.optim.Adam(net.parameters(), lr=float(cfg["lstm"]["lr"]))
    loss_fn = nn.CrossEntropyLoss(ignore_index=stoi["<pad>"])

    net.train()
    for _epoch in range(int(cfg["lstm"]["epochs"])):
        for xb, yb in dl:
            xb = xb.to(device)
            yb = yb.to(device)
            logits = net(xb)
            B, T, V = logits.shape
            loss = loss_fn(logits.reshape(B * T, V), yb.reshape(B * T))
            opt.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(net.parameters(), 1.0)
            opt.step()

    return LSTMCharModel(stoi=stoi, itos=itos, net=net, max_len=max_len)

