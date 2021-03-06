import matplotlib.pyplot as plt
import numpy as np

import deepscratch.learning.losses as losses
import deepscratch.learning.metrics as ds_metrics
import deepscratch.models.optimizers as optimizers


class Trainer(object):
    def __init__(self, model, loss, metrics=[], print_step_mod=1000, verbose=True):
        self.model = model
        self.model.initialize()

        self.loss = losses.load(loss) if type(loss) is str else loss
        self.metrics = self._define_metrics(metrics)

        self.train_step = 0
        self.eval_steps = []
        
        self.verbose = verbose
        self.print_step_mod = print_step_mod
        
        self.train_losses = []
        self.eval_losses = []
    

    def _define_metrics(self, metrics):
        new_metrics = []
        for metric in metrics:
            new_metrics.append(ds_metrics.load(metric) if type(metric) is str else metric)
        return new_metrics


    def batch_train(self, batch_x, batch_y):
        self.train_step += 1
        # run feed forward network
        pred_y = self.model.forward(batch_x)
        # save loss
        self.train_losses.append(self.loss(pred_y, batch_y))
        # run backpropagation
        self.model.backward(self.loss.grads(pred_y, batch_y))
        if self.verbose and (self.train_step - 1) % self.print_step_mod == 0:
            print('Loss: %.4f for step %d' % (self.train_losses[-1], self.train_step))
    

    def batches(self, x, y, batch_size=True):
        idx = np.random.permutation(len(x))
        x = x[idx]
        y = y[idx]
        
        for i in range(0, len(x)-batch_size-1, batch_size):
            batch_x = x[i:i+batch_size]
            batch_y = y[i:i+batch_size]
            yield batch_x, batch_y


    def train(self, data_x, data_y, epochs=1):
        for epoch in range(1, epochs + 1):
            for batch_x, batch_y in self.batches(data_x, data_y, 16):
                self.batch_train(batch_x, batch_y)

    def eval(self, data_x, data_y, metrics=None):
        # run feed forward network
        pred_y = self.model.forward(data_x)
        
        # loss
        loss = self.loss(pred_y, data_y)
        self.eval_losses.append(loss)
        
        # metrics
        if metrics is None:
            metrics = self.metrics
        res_metrics = []
        
        for metric in metrics:
            res_metrics.append(metric(pred_y, data_y))
        
        self.eval_steps.append(self.train_step)    
        return loss, res_metrics

    
    def plot_losses(self):
        if len(self.eval_losses) > 0:
            plt.title('Train Loss: %.4f | Test Loss: %.4f for step %d' % (self.train_losses[-1], self.eval_losses[-1], self.train_step))
        else:
            plt.title('Train Loss: %.4f for step %d' % (self.train_losses[-1], self.train_step))    
        plt.plot([i for i in range(self.train_step)], self.train_losses)
        plt.plot([i for i in self.eval_steps], self.eval_losses)