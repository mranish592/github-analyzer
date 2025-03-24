import { ScrollArea } from "@radix-ui/react-scroll-area"
import { Textarea } from "./ui/textarea"




export function JsonResponseViewer ({response} : {response: string}) {
    const parsed = JSON.parse(response);
    const formatted = JSON.stringify(parsed, null, 2);
    return (
        <>
            <ScrollArea className="w-full rounded-md border border-gray-800 bg-gray-950">
                <div className="p-4">
                    <Textarea
                        readOnly
                        value={formatted}
                        className="w-full min-h-[300px] bg-gray-900 text-gray-200 border-gray-800 font-mono text-sm whitespace-pre-wrap" // added whitespace-pre-wrap
                        placeholder="Formatted JSON will appear here..."
                    />
                
                </div>
            </ScrollArea>
        </>
    )
}