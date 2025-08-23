# mcp/message_protocol.py

class MCPMessage:
    """
    Message Control Protocol - Simple communication system between process
    Think of this like an email system where it send structured messages for each process
    Each message has clear sender, receiver, type, and content (payload)
    """
    
    def __init__(self, sender, receiver, msg_type, trace_id, payload):
        """
        Create a new message between process
        Args:
            sender: Which process is sending this message
            receiver: Which process should receive this message
            msg_type: What type of request/response this is (e.g., "DOCUMENT_UPLOAD")
            trace_id: Unique ID to track this request through the entire system
            payload: The actual data being sent (dictionary with relevant info)
        """
        self.sender = sender        # Who sent this message
        self.receiver = receiver    # Who should receive this message
        self.type = msg_type       # What kind of message this is
        self.trace_id = trace_id   # Unique identifier for tracking
        self.payload = payload     # The actual data/content

    def to_dict(self):
        """
        Convert message to dictionary format (useful for logging and debugging)
        Returns:
            Dictionary representation of the message
        """
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "type": self.type,
            "trace_id": self.trace_id,
            "payload": self.payload
        }

    @staticmethod
    def from_dict(data):
        """
        Create a message from dictionary data (useful when loading from files/databases)
        Args:
            data: Dictionary containing message data
        Returns:
            MCPMessage object created from the dictionary
        """
        return MCPMessage(
            sender=data["sender"],
            receiver=data["receiver"],
            msg_type=data["type"],
            trace_id=data["trace_id"],
            payload=data["payload"]
        )
