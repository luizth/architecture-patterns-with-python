import abc

import model


class AbstractRepository(abc.ABC):

    @abc.abstractmethod  # Python will refuse to let you instantiate a class that does not implement all the abstractmethods defined in its parent class.
    def add(self, batch: model.Batch):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, reference) -> model.Batch:
        raise NotImplementedError
