import { useRef, useEffect } from 'react';
import { ChatHeader } from './ChatHeader';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';
import { EmptyState } from './EmptyState';
import { TypingIndicator } from './TypingIndicator';
import { useChat } from '@/hooks/useChat';
import { ScrollArea } from '@/components/ui/scroll-area';

export const ChatInterface = () => {
    const { messages, isLoading, sendMessage, clearChat } = useChat();
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages, isLoading]);

    return (
        <div className="flex h-screen flex-col bg-background">
            <ChatHeader onClearChat={messages.length > 0 ? clearChat : undefined} />

            <ScrollArea className="flex-1" ref={scrollRef}>
                <div className="max-w-4xl mx-auto">
                    {messages.length === 0 ? (
                        <EmptyState />
                    ) : (
                        <div className="py-4">
                            {messages.map((message) => (
                                <ChatMessage key={message.id} message={message} />
                            ))}
                            {isLoading && <TypingIndicator />}
                        </div>
                    )}
                </div>
            </ScrollArea>

            <ChatInput onSend={sendMessage} isLoading={isLoading} />
        </div>
    );
};
