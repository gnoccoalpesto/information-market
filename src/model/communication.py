import copy

from model.navigation import Location, Target
from helpers.utils import rotate, CommunicationState, NoInformationSoldException, get_orientation_from_vector
from model.payment import Transaction


class CommunicationSession:
    def __init__(self, client, neighbors):
        self._client = client
        self._neighbors = {n.id: n for n in neighbors if n.comm_state == CommunicationState.OPEN}


    def get_metadata(self, location):#,payment_database):
        #TODO also, should this be retrieved from bchain to avoid lying?
        #TODO should differentiate if using local or global information, passing bchain?
        metadata = {n_id:{"age": n.get_info_from_behavior(location).get_age(),
                            # "reward": payment_database.get_reward(n_id),#(n_id, location), if different rewards
                        }
                        for n_id, n in self._neighbors.items() 
                        if n.get_info_from_behavior(location) is not None 
                            and n.get_info_from_behavior(location).is_valid()
                            #TODO validity on blockchain
                    }
        return metadata


    def record_attempted_transaction(self):
        self._client.record_attempted_transaction()

    
    def record_validated_transaction(self):
        self._client.record_validated_transaction()


    def make_transaction(self, neighbor_id, location) -> Target:
        target = copy.deepcopy(self._neighbors[neighbor_id].get_info_from_behavior(location))
        if target is None:
            raise NoInformationSoldException
        target.rotate(self._neighbors[neighbor_id].orientation - self._client.orientation)
        transaction = Transaction(self._client.id,
                                  neighbor_id,
                                  location,
                                  get_orientation_from_vector(target.get_distance()),
                                  None)
        self._client.record_completed_transaction(transaction)
        self._client.communication_happened()
        self._neighbors[neighbor_id].communication_happened()
        return target


    def record_combined_transaction(self):
        self._client.record_combined_transaction()


    def get_distance_from(self, neighbor_id):
        distance = self._neighbors[neighbor_id].pos - self._client.pos
        return rotate(distance, -self._client.orientation)


    def get_own_reward(self):
        return self._client.reward()


    def get_neighbor_reward(self, neighbor_id):
        return self._neighbors[neighbor_id].reward()


    def get_average_neighbor_reward(self):
        return sum([n.reward() for n in self._neighbors.values()]) / len(self._neighbors)


    def get_max_neighboor_reward(self):
        return max([n.reward() for n in self._neighbors.values()])


    def get_min_neighboor_reward(self):
        return min([n.reward() for n in self._neighbors.values()])

        