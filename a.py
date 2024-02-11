from datasets import Dataset, load_from_disk

dt = load_from_disk("data/hincal-uluc_dataset_242")

print(len(dt))