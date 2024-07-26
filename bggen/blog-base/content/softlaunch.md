Title: Extremely soft blog launch!
Date: 2023-06-03 00:00
Category: About
Tags: About
Authors: Michael Saxon
Summary: To test that my blog implementation works, I'll share my pytorchlightning-based replication of dataset cartography!

### About my blog

I have thoughts I'd like to share from time-to-time. I have been testing my Pelican-based blog generator for a while and got it working, but a lack of fully-formed blogpost ideas to upload has consequently kept me from updating my website for months. This has become a problem for me as news and results have accumulated. Thus at this point, I have no choice but to push a placeholder blogpost such as this. Looking forward to making a more substantial post soon 🫡

### Implemented in PL

Check out this code! You can pass in any `Callback` object from pytorch lightning, to track the training process of a model in pytorch lightning. This automatically collects the training dynamics statistics and writes them to a given output csv file for future processing and analysis!

```python
class CartographyCallback(Callback):
    def __init__(self, output_base):
        super().__init__()
        self.output_base = output_base

    def init_buffers(self, trainer):
        key_nums = {
            "train" : len(trainer.datamodule.train),
            "val" : len(trainer.datamodule.valid),
            "test" : len(trainer.datamodule.test)
        }
        self.confidences = define_samplewise_metric(key_nums)
        self.correctnesses = define_samplewise_metric(key_nums)

    def cartography_save(self, epoch, key):
        np.save(f"{self.output_base}/conf_{key}_{epoch}.npy", self.confidences[key])
        np.save(f"{self.output_base}/corr_{key}_{epoch}.npy", self.correctnesses[key])

    def batch_end_accumulate(self, batch, outputs, key):
        targets = batch['labels'].squeeze()
        logits = outputs['logits']
        preds = torch.max(logits, dim=-1).indices
        batch_idces = batch['idx'].cpu().numpy().squeeze()
        self.confidences[key][batch_idces] = confidence_elementwise(targets, logits).squeeze()
        self.correctnesses[key][batch_idces] = correct_elementwise(targets, preds).squeeze()

    def on_train_batch_end(self, trainer, pl_module, outputs, batch, batch_idx):
        self.batch_end_accumulate(batch, outputs, "train")

    def on_validation_batch_end(self, trainer, pl_module, outputs, batch, batch_idx, dataloader_idx):
        self.batch_end_accumulate(batch, outputs, "val")

    def on_test_batch_end(self, trainer, pl_module, outputs, batch, batch_idx, dataloader_idx):
        self.batch_end_accumulate(batch, outputs, "test")

    def on_train_epoch_end(self, trainer, pl_module):
        self.cartography_save(trainer.current_epoch, "train")

    def on_validation_epoch_end(self, trainer, pl_module):
        self.cartography_save(trainer.current_epoch, "val")

    def on_test_epoch_end(self, trainer, pl_module):
        self.cartography_save(trainer.current_epoch, "test")

    def on_train_start(self, trainer, pl_module):
        self.init_buffers(trainer)

    def on_sanity_check_start(self, trainer, pl_module):
        self.init_buffers(trainer)
```

I wrote this code so that I could replicate the [Dataset Cartography](https://arxiv.org/abs/2009.10795) features of confidence and correctness to analyze the effectiveness of my [PECO](https://arxiv.org/abs/2112.09237) tool for analyzing datasets. You can see the code used in-context [here!](https://github.com/michaelsaxon/DatasetAnalysis)
