"""
Rational Activation Functions for tensorflow/keras
==================================================

This module allows you to create Rational Neural Networks using Learnable
Rational activation functions.
"""
from tensorflow.keras.layers import Layer
import tensorflow as tf

from rational.keras.versions import _version_a, _version_b, _version_c, _version_d
from rational.utils.get_weights import get_parameters


class Rational(Layer):
    """
    Inherited from tensorflow.keras.layers.Layer

    Defines custom layer attributes, and creates layer state variables that do not depend on
    input shapes, using ``add_weight()``

    Arguments:
            approx_func (str):
                The name of the approximated function for initialisation. \
                The different functions are available in `rational.rationals_config.json`. \n
                Default ``leaky_relu``
            degrees (tuple of int):
                The degrees of the numerator (P) and denominator (Q).\n
                Default ``(5, 4)``
            cuda (bool):
                whether to execute on cuda device. NOTE: CURRENTLY NOT USED, i.e. \
                function always executes on cuda device if available.
            version (str):
                Version of Rational to use. Rational(x) = P(x)/Q(x)\n
                `A`: Q(x) = 1 + \|b_1.x\| + \|b_2.x\| + ... + \|b_n.x\|\n
                `B`: Q(x) = 1 + \|b_1.x + b_2.x + ... + b_n.x\|\n
                `C`: Q(x) = 0.1 + \|b_1.x + b_2.x + ... + b_n.x\|\n
                `D`: like `B` with noise\n
                Default ``A``
            trainable (bool):
                If the weights are trainable, i.e, if they are updated during \
                backward pass. \n
                Default ``True``
    """
    def __init__(self, approx_func="leaky_relu", degrees=(5, 4), cuda=False, version="A",
                 trainable=True):
        super(Rational, self).__init__()

        w_numerator, w_denominator = get_parameters(version, degrees, approx_func)

        # add trainable weight vectors for numerator (a_0, ... a_n) and denominator (b_0, ... b_m)
        self.numerator = self.add_weight(shape=(len(w_numerator),), name='w_numerator',
                                         trainable=trainable,
                                         initializer=tf.keras.initializers.Constant(w_numerator))

        self.denominator = self.add_weight(shape=(len(w_denominator),), name='w_denominator',
                                           trainable=trainable,
                                           initializer=tf.keras.initializers
                                           .Constant(w_denominator))

        # record whether weights are trainable. Used later by call() method
        self.training = trainable

        # set rational activation function version
        self.rational_func = {'A': _version_a, 'B': _version_b, 'C': _version_c, 'D': _version_d}\
            .get(version)
        if self.rational_func is None:
            raise ValueError("rational activation function version %s not implemented" % version)

    def build(self, input_shape):
        """
        Inherited from tensorflow.keras.layers.Layer

        This method can be used to create weights that depend on the shape(s) of the input(s),
        using ``add_weight()``. ``__call__()`` will automatically build the layer (if it has not
        been built yet) by calling ``build()``.

        Arguments:
            input_shape (TensorShape):
                or list of instances of `TensorShape` if
                the layer expects a list of inputs (one instance per input).
        """
        super(Rational, self).build(input_shape)

    def call(self, inputs, **kwargs):
        """
        Inherited from tensorflow.keras.layers.Layer

        Called in ``__call__`` after making sure ``build()`` has been called. ``call()`` performs
        the logic of applying the layer to the input tensors (which should be passed in as
        argument). Two reserved keyword arguments you can optionally use in ``call()`` are:

        - training (boolean, whether the call is in inference mode or training mode)
        - mask (boolean tensor encoding masked timesteps in the input, used in RNN layers)

        Arguments:
                inputs:
                    Input tensorflow tensor
        Returns:
                output tensor, with the respective rational activation function applied to it
        """
        return self.rational_func(inputs, self.numerator, self.denominator, self.training)
