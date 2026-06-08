// Chatdelete.test.js
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import ConversationDelete from '../components/Chatdelete'; // Adjust the import path as needed

describe('ConversationDelete Component', () => {
    const mockOnClose = jest.fn();
    const mockOnConfirm = jest.fn();
    const conversationName = 'Test Conversation';

    beforeEach(() => {
        jest.clearAllMocks();
    });

    test('should display the modal with the correct title and conversation name', () => {
        render(
            <ConversationDelete
                show={true}
                onClose={mockOnClose}
                onConfirm={mockOnConfirm}
                conversationName={conversationName}
            />
        );

        // Check if the modal title and body text are rendered correctly
        expect(screen.getByText('Delete chat?')).toBeInTheDocument();
        expect(screen.getByText(`This will delete ${conversationName}`)).toBeInTheDocument();
    });

    test('should call onClose when the cancel button is clicked', () => {
        render(
            <ConversationDelete
                show={true}
                onClose={mockOnClose}
                onConfirm={mockOnConfirm}
                conversationName={conversationName}
            />
        );

        const cancelButton = screen.getByText('Cancel');
        fireEvent.click(cancelButton);

        expect(mockOnClose).toHaveBeenCalledTimes(1);
    });

    test('should call onConfirm and onClose when the delete button is clicked', () => {
        render(
            <ConversationDelete
                show={true}
                onClose={mockOnClose}
                onConfirm={mockOnConfirm}
                conversationName={conversationName}
            />
        );

        const deleteButton = screen.getByText('Delete');
        fireEvent.click(deleteButton);

        expect(mockOnConfirm).toHaveBeenCalledTimes(1);
        expect(mockOnClose).toHaveBeenCalledTimes(1);
    });

    test('should not render the modal when show is false', () => {
        render(
            <ConversationDelete
                show={false}
                onClose={mockOnClose}
                onConfirm={mockOnConfirm}
                conversationName={conversationName}
            />
        );

        expect(screen.queryByText('Delete chat?')).not.toBeInTheDocument();
    });

    test('should render modal with custom class names', () => {
        render(
            <ConversationDelete
                show={true}
                onClose={mockOnClose}
                onConfirm={mockOnConfirm}
                conversationName={conversationName}
            />
        );

        const modal = screen.getByRole('dialog');
        expect(modal).toHaveClass('custom-modal');
    });
});
