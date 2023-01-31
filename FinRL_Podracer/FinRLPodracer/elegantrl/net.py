import numpy as np
import torch
import torch.nn as nn


class ActorPPO(nn.Module):
    def __init__(self, mid_dim, state_dim, action_dim):
        """
        Initialize the action layer

        Args:
            self: write your description
            mid_dim: write your description
            state_dim: write your description
            action_dim: write your description
        """
        super().__init__()
        self.net = nn.Sequential(nn.Linear(state_dim, mid_dim), nn.ReLU(),
                                 nn.Linear(mid_dim, mid_dim // 2), nn.ReLU(),
                                 nn.Linear(mid_dim // 2, action_dim), )
        layer_norm(self.net[-1], std=0.1)  # output layer for action

        # the logarithm (log) of standard deviation (std) of action, it is a trainable parameter
        self.a_logstd = nn.Parameter(torch.zeros((1, action_dim)) - 0.5, requires_grad=True)
        self.sqrt_2pi_log = np.log(np.sqrt(2 * np.pi))

    def forward(self, state):
        """
        Returns the tangent of the given state.

        Args:
            self: write your description
            state: write your description
        """
        return self.net(state).tanh()  # action.tanh()

    def get_action(self, state):
        """
        Get action and noise

        Args:
            self: write your description
            state: write your description
        """
        a_avg = self.net(state)
        a_std = self.a_logstd.exp()

        noise = torch.randn_like(a_avg)
        action = a_avg + noise * a_std.expand_as(a_avg)
        return action, noise

    def get_logprob_entropy(self, state, action):
        """
        Get logprob and policy entropy for given state and action.

        Args:
            self: write your description
            state: write your description
            action: write your description
        """
        a_avg = self.net(state)
        a_std = self.a_logstd.exp()

        delta = ((a_avg - action) / a_std).pow(2) * 0.5
        logprob = -(self.a_logstd + self.sqrt_2pi_log + delta).sum(1)  # new_logprob

        dist_entropy = (logprob.exp() * logprob).mean()  # policy entropy
        return logprob, dist_entropy

    def get_old_logprob(self, _action, noise):  # noise = action - a_noise
        """
        Get the log probability of the action given the noise.

        Args:
            self: write your description
            _action: write your description
            noise: write your description
        """
        delta = noise.pow(2) * 0.5
        return -(self.a_logstd + self.sqrt_2pi_log + delta).sum(1)  # old_logprob


class CriticPPO(nn.Module):
    def __init__(self, mid_dim, state_dim, _action_dim, if_use_dn=False):
        """
        Initialize the model.

        Args:
            self: write your description
            mid_dim: write your description
            state_dim: write your description
            _action_dim: write your description
            if_use_dn: write your description
        """
        super().__init__()
        if if_use_dn:
            nn_dense = DenseNet(mid_dim // 2)
            inp_dim = nn_dense.inp_dim
            out_dim = nn_dense.out_dim

            self.net = nn.Sequential(nn.Linear(state_dim, inp_dim), nn.ReLU(),
                                     nn_dense,
                                     nn.Linear(out_dim, 1), )
        else:
            self.net = nn.Sequential(nn.Linear(state_dim, mid_dim), nn.ReLU(),
                                     nn.Linear(mid_dim, mid_dim // 2), nn.ReLU(),
                                     nn.Linear(mid_dim // 2, 1), )
        layer_norm(self.net[-1], std=0.5)  # output layer for Q value

    def forward(self, state):
        """
        Forward computation.

        Args:
            self: write your description
            state: write your description
        """
        return self.net(state)  # Q value


"""utils"""


class NnReshape(nn.Module):
    def __init__(self, *args):
        """
        Initialize the instance with the given arguments.

        Args:
            self: write your description
        """
        super().__init__()
        self.args = args

    def forward(self, x):
        """
        Forward pass through the sequence x applying the filter.

        Args:
            self: write your description
            x: write your description
        """
        return x.view((x.size(0),) + self.args)


class DenseNet(nn.Module):  # plan to hyper-param: layer_number
    def __init__(self, lay_dim):
        """
        Initialize the layer for the lay_dim

        Args:
            self: write your description
            lay_dim: write your description
        """
        super().__init__()
        self.dense1 = nn.Sequential(nn.Linear(lay_dim * 1, lay_dim * 1), nn.Hardswish())
        self.dense2 = nn.Sequential(nn.Linear(lay_dim * 2, lay_dim * 2), nn.Hardswish())
        self.inp_dim = lay_dim
        self.out_dim = lay_dim * 4

    def forward(self, x1):  # x1.shape==(-1, lay_dim*1)
        """
        Forward pass through the network

        Args:
            self: write your description
            x1: write your description
        """
        x2 = torch.cat((x1, self.dense1(x1)), dim=1)
        x3 = torch.cat((x2, self.dense2(x2)), dim=1)
        return x3  # x2.shape==(-1, lay_dim*4)


def layer_norm(layer, std=1.0, bias_const=1e-6):
    """
    Layer normalizer.

    Args:
        layer: write your description
        std: write your description
        bias_const: write your description
    """
    torch.nn.init.orthogonal_(layer.weight, std)
    torch.nn.init.constant_(layer.bias, bias_const)
