"use client"

import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import { z } from "zod"

import { Button } from "@/components/ui/button"
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import api from "@/api/api"

const FormSchema = z.object({
  username: z.string().min(1, {
    message: "Username must be at least 1 characters.",
  }),
})

export function UsernameForm({ show, setShow, setReponse }: { show: boolean, setShow: (show: boolean) => void, setReponse: (response: string) => void }) {
  const form = useForm<z.infer<typeof FormSchema>>({
    resolver: zodResolver(FormSchema),
    defaultValues: {
      username: "",
    },
  })

  function onSubmit(data: z.infer<typeof FormSchema>) {
    console.log(data)
    api.get(`/analyze/${data.username}`)
        .then((response) => {
            console.log(response.data)
            setReponse(JSON.stringify(response.data))
            setShow(true)
        }).catch((error) => {
            console.error(error)
            setReponse("An error occurred")
            setShow(true)
        })
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="w-1/2 space-y-6">
        <FormField
          control={form.control}
          name="username"
          render={({ field }) => (
            <FormItem>
              <FormLabel className="">Username</FormLabel>
              <FormControl>
                <div  className="w-1/2">
                <Input placeholder="https://github.com/torvalds" {...field} />
                </div>
              </FormControl>
              <FormDescription>
                Enter a GitHub username or link to analyze their profile.
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit">Analyze</Button>
      </form>
    </Form>
  )
}
