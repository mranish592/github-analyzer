import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
  } from "@/components/ui/card"
import { cn } from "@/lib/utils"

export function AnalyzeResponse({ response, show } : { response: string, show: boolean }) {
    if(!show) return <></>
    return (
        <div className={cn("mt-12 w-1/3")}>
        <Card>
            <CardHeader>
            <CardTitle>Analysis Results</CardTitle>
            </CardHeader>
            <CardContent>
            <CardDescription>
                Analysis
            </CardDescription>
            <p>{response}</p>
            </CardContent>
        </Card>
      </div>
    )
}