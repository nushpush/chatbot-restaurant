import React from 'react';
import { Modal, Button } from 'react-bootstrap';
import './Chatdelete.css';
const ConversationDelete = ({ show, onClose, onConfirm, conversationName }) => {
  return (
    <Modal show={show} onHide={onClose} className="custom-modal">
      <Modal.Header closeButton>
        <Modal.Title >Delete chat?</Modal.Title>
      </Modal.Header>
      <Modal.Body>
      This will delete <strong>{conversationName}</strong>
      </Modal.Body>
      <Modal.Footer>
        <Button  className="cancel-btn" onClick={onClose}>
          Cancel
        </Button>
        <Button  className="delete-btn" onClick={() => {
          onConfirm();
          onClose();
        }}>
          Delete
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default ConversationDelete;
