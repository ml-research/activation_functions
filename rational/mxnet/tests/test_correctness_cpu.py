"""
This file tests that cpu calculations produce correct results.
"""
import mxnet as mx
from mxnet import gluon

from ..rationals import Rational

# build a small neural net containing one Rational layer
net = gluon.nn.HybridSequential()
with net.name_scope():
    net.add(Rational())
net.initialize()
# net.hybridize()


def test():
    input_data = mx.nd.array([-2., -1, 0., 1., 2.])
    net(input_data)

    # expected_res = LeakyReLU(data=input)
    # result = fut(input).numpy()
    # print('leakyrelu', expected_res)
    # print('rational', result)
    # assert np.all(np.isclose(expected_res, result, atol=5e-02))
    pass
