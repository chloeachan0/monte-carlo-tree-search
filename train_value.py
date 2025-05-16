# train_value.py
import pickle, torch, torch.nn as nn, torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


class ValueNet(nn.Module):
    def __init__(self, in_dim=54):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, 256),
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 1),
            nn.Tanh(),  # output in (-1,1)
        )

    def forward(self, x):
        return self.net(x).squeeze(-1)


if __name__ == "__main__":  # this breaks without this

    vecs, zs = zip(*pickle.load(open("selfplay_10000g_0.05s.pkl", "rb")))
    X = torch.tensor(vecs, dtype=torch.float32)
    y = torch.tensor(zs, dtype=torch.float32)
    dataset = TensorDataset(X, y)
    loader = DataLoader(dataset, batch_size=2048, shuffle=True)

    net = ValueNet().to(DEVICE)
    opt = optim.Adam(net.parameters(), lr=3e-4)
    loss_fn = nn.MSELoss()

    for epoch in range(25):
        for xb, yb in loader:
            xb, yb = xb.to(DEVICE), yb.to(DEVICE)
            pred = net(xb)
            loss = loss_fn(pred, yb)
            opt.zero_grad()
            loss.backward()
            opt.step()
        print(f"epoch {epoch:02d}  loss {loss.item():.4f}")

    torch.save(net.state_dict(), "value_net.pt")
