import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
  } from "@/components/ui/card"
import { cn } from "@/lib/utils"
import { JsonResponseViewer } from "./JsonResponseViewer"

export function AnalyzeResponse({ response, show } : { response: string, show: boolean }) {
    if(!show) return <></>
    return (
        <div className={cn("mt-12 w-1/2")}>
        <Card>
            <CardHeader>
            <CardTitle>Analysis Results</CardTitle>
            </CardHeader>
            <CardContent>
            <CardDescription>
                Analysis
            </CardDescription>
            <JsonResponseViewer response={response} />
            {/* <p>{response}</p> */}
            </CardContent>
        </Card>
      </div>
    )
}