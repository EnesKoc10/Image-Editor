import './globals.css'

export const metadata = {
  title: 'Image Editor',
  description: 'Image processing application',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body suppressHydrationWarning>
        {children}
      </body>
    </html>
  )
}