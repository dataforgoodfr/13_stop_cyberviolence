import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { CheckCircle, Circle, MessageSquare, Send } from "lucide-react";
import { useState } from "react";
import { useChatMessages } from '@chainlit/react-client';

export default function FeedbackWidget() {
    const { feedback = null, comment = "" } = props;
    const { messages, firstInteraction, threadId } = useChatMessages();
    const [selectedFeedback, setSelectedFeedback] = useState(feedback);
    const [userComment, setUserComment] = useState(comment);
    const [sending, setSending] = useState(false);
    const [sent, setSent] = useState(false);
    const [disabled, setDisabled] = useState(false);

    const handleSelect = (value) => {
        setSelectedFeedback(value);
    };

    const handleCommentChange = (e) => {
        setUserComment(e.target.value);
    };

    const handleSend = async () => {
        setSending(true);
        setDisabled(true);
        // Update the element's props in Chainlit
        await updateElement({ ...props, feedback: selectedFeedback, comment: userComment, thread_id: threadId });

        // Call Python action in Chainlit
        await callAction({
            name: "handle_feedback",
            payload: { feedback: selectedFeedback, comment: userComment, thread_id : threadId }
        });
        setSending(false);
        setSent(true);
    };

    const RatingButton = ({ value }) => (
        <Button
            variant="ghost"
            className="w-8 h-8 p-0 flex flex-col items-center justify-center"
            onClick={() => handleSelect(value)}
            disabled={disabled || sent}
        >
            {selectedFeedback === value ? <CheckCircle className="mr-0 text-xs" /> : <Circle className="mr-0 text-xs" />}

            <span className="text-xs">{value}</span>
                    </Button>
    );

    return (
        <div className="space-y-3 relative" style={{pointerEvents: sending ? 'none' : 'auto'}}>
            {sending && (
                <div className="absolute inset-0 bg-gray-500 bg-opacity-50 z-10 flex items-center justify-center">
                    <div className="text-white text-lg">Sending...</div>
                </div>
            )}
            {sent && (
                <Card className="p-3 text-sm text-green-500 bg-green-50 border border-green-200">
                    Feedback sent! Thank you.
                </Card>
            )}
            <Card className="flex flex-col items-center justify-between p-3">
                <div className="flex items-center space-x-2 w-full mb-2">
                    <span className="font-medium text-sm">Rate from 1 to 10</span>
                </div>
                <div className="flex space-x-2">
                    {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((value) => (
                        <RatingButton key={value} value={value} />
                    ))}
                </div>
            </Card>
            <Card className="flex items-center p-3">
                <MessageSquare className="mr-2 text-gray-400" />
                <textarea
                    className="flex-1 border-none outline-none bg-transparent text-sm"
                    placeholder="Add a comment (optional)"
                    value={userComment}
                    onChange={handleCommentChange}
                    rows={2}
                    disabled={disabled || sent}
                />
            </Card>
            <div className="flex justify-end">
                <Button
                    onClick={handleSend}
                    disabled={sending || !selectedFeedback || sent || disabled}
                    className="flex items-center"
                >
                    <Send className="mr-1" />
                    {sending ? "Sending..." : sent ? "Sent!" : "Send"}
                </Button>
            </div>
        </div>
    );
}
