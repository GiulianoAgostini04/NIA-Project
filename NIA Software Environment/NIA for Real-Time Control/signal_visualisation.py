# Importing Boardshim as principal class that manage the communication with the EEG board
# Importing BrainFlowInput Params in order to contain the connection parameter
# Importing BoardIds in order to identify the supported acquisition board
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds

# Defining the model class that contains data and function linked to the same thing
class EEGAcquisition:
    # The code runs automatically when the object is created
    def __init__(self, use_synthetic=True, serial_port=None):

        # Saving the container of parameters
        self.params = BrainFlowInputParams()
        
        # Conditional logic, in order to make the code function with the synthetic board and/or the physical one
        if use_synthetic:
            self.board_id = BoardIds.SYNTHETIC_BOARD.value
        else:
            self.board_id = BoardIds.GANGLION_NATIVE_BOARD.value
            # mac_address left empty: BrainFlow will autodiscover the Ganglion
            
        # Creating the object that will communicate with the board        
        self.board = BoardShim(self.board_id, self.params)
        # Parameters that will be shareb during the communication
        self.sampling_rate = BoardShim.get_sampling_rate(self.board_id)
        self.eeg_channels = BoardShim.get_eeg_channels(self.board_id)
        # Creating the flag in order to check whether the streaming is active or not
        self.is_streaming = False
    
    # Opening the communication with the board
    def connect(self):
        try:
            self.board.prepare_session()
        except Exception as e:
            raise ConnectionError("Impossible connecting to the board. "
                                  "Please verify that the dongle connection."
            ) from e
    
    # Starting the continuous acquisition
    def start_stream(self):
        self.board.start_stream()
        self.is_streaming = True
    
    # Taking the latest samples from the buffer without voiding it
    def get_latest_data(self, n_samples):
        # Sampling the latest samples without dumping the buffer
        return self.board.get_current_board_data(n_samples)
     # Stopping the streaming whethert the latter was active
    def stop_stream(self):
        if self.is_streaming:
            self.board.stop_stream()
            self.is_streaming = False
    
    # Closing of the session and making free the resources
    def disconnect(self):
        self.board.release_session()