from datasets import load_dataset, DatasetDict, concatenate_datasets
import os

ds = load_dataset("nvidia/CantTalkAboutThis-Topic-Control-Dataset")

# Filter-in the desired domains only
keep_domains = {"insurance", "real estate", "travel"}
def keep_batch(batch):
    return [d in keep_domains for d in batch["domain"]]

# Filter each split
train_f = ds["train"].filter(keep_batch, batched=True)
test_f  = ds["test"].filter(keep_batch, batched=True)

# Save trainset
train_f.to_csv("data/cta_re_ins_travel_train.csv")
