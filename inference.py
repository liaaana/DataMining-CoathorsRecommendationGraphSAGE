import torch
import pickle
from torch_geometric.nn import SAGEConv
import torch.nn as nn
import torch.nn.functional as F

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

with open("prep/author_mappings.pkl", "rb") as f:
    mappings = pickle.load(f)
author2idx = mappings["author2idx"]
idx2author = mappings["idx2author"]

node_feats = torch.load("prep/node_features.pt").to(device)
edge_idx = torch.load("prep/edge_index.pt").to(device)

class GraphSAGE_LinkPredictor(nn.Module):
    def __init__(self, in_ch, hid_ch, layers, dp):
        super().__init__()
        self.convs = nn.ModuleList(
            [SAGEConv(in_ch, hid_ch)] + [SAGEConv(hid_ch, hid_ch) for _ in range(layers - 1)]
        )
        self.dp = dp
        feat_dim = hid_ch * 2 + in_ch  
        self.mlp = nn.Sequential(
            nn.Linear(feat_dim, hid_ch),
            nn.ReLU(),
            nn.Linear(hid_ch, 1)
        )

    def encode(self, x, ei):
        for c in self.convs:
            x = F.relu(c(x, ei))
            x = F.dropout(x, p=self.dp, training=self.training)
        return x

    def decode(self, z, ep, ea):
        u, v = ep
        h = torch.cat([z[u], z[v], ea], dim=1)
        return self.mlp(h).squeeze()

hid, hc, nl, dp = node_feats.size(1), 64, 3, 0.3 
model = GraphSAGE_LinkPredictor(hid, hc, nl, dp).to(device)
model.load_state_dict(torch.load("prep/gnn_link_predictor.pth", map_location=device, weights_only=True))
model.eval()

with torch.no_grad():
    z = model.encode(node_feats, edge_idx)

def get_recommendations(author_name, topk=5):
    if author_name not in author2idx:
        return []

    u = author2idx[author_name]
    all_vs = torch.arange(z.size(0), device=device)
    cand_vs = all_vs[all_vs != u]

    src = u * torch.ones_like(cand_vs)
    edge_pairs = torch.stack([src, cand_vs], dim=0)
    ea = 0.5 * (node_feats[u].unsqueeze(0) + node_feats[cand_vs])

    with torch.no_grad():
        logits = model.decode(z, edge_pairs, ea)

    top_logits, top_idx = torch.topk(logits, min(topk, logits.size(0)))
    top_vs = cand_vs[top_idx]

    recommendations = [
        [idx2author[int(v)], round(float(s), 4)]
        for v, s in zip(top_vs, top_logits)
    ]
    return recommendations
