"use client"

import * as React from "react"
import { cn } from "@/lib/utils"

interface PopoverProps {
  children: React.ReactNode
}

interface PopoverTriggerProps {
  children: React.ReactNode
  onClick?: () => void
}

interface PopoverContentProps {
  children: React.ReactNode
  className?: string
  align?: "start" | "center" | "end"
  sideOffset?: number
}

const PopoverContext = React.createContext<{
  isOpen: boolean
  setIsOpen: (open: boolean) => void
}>({
  isOpen: false,
  setIsOpen: () => {},
})

const Popover: React.FC<PopoverProps> = ({ children }) => {
  const [isOpen, setIsOpen] = React.useState(false)

  return (
    <PopoverContext.Provider value={{ isOpen, setIsOpen }}>
      <div className="relative">{children}</div>
    </PopoverContext.Provider>
  )
}

const PopoverTrigger: React.FC<PopoverTriggerProps> = ({ children, onClick }) => {
  const { isOpen, setIsOpen } = React.useContext(PopoverContext)

  const handleClick = () => {
    setIsOpen(!isOpen)
    onClick?.()
  }

  return (
    <div onClick={handleClick} className="cursor-pointer">
      {children}
    </div>
  )
}

const PopoverContent: React.FC<PopoverContentProps> = ({ 
  children, 
  className, 
  align = "center", 
  sideOffset = 4 
}) => {
  const { isOpen } = React.useContext(PopoverContext)

  if (!isOpen) return null

  return (
    <div
      className={cn(
        "absolute z-50 w-72 rounded-md border bg-white p-4 shadow-md outline-none",
        "top-full mt-2", // Default positioning
        align === "start" && "left-0",
        align === "center" && "left-1/2 -translate-x-1/2",
        align === "end" && "right-0",
        className
      )}
    >
      {children}
    </div>
  )
}

export { Popover, PopoverTrigger, PopoverContent } 