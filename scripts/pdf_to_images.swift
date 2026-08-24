import Foundation
import PDFKit
import AppKit

guard CommandLine.arguments.count >= 3 else {
    print("Usage: swift pdf_to_images.swift <input.pdf> <output_dir> [prefix]")
    exit(1)
}

let pdfPath = CommandLine.arguments[1]
let outputDir = CommandLine.arguments[2]
let prefix = CommandLine.arguments.count >= 4 ? CommandLine.arguments[3] : ""

let pdfUrl = URL(fileURLWithPath: pdfPath)
guard let doc = PDFDocument(url: pdfUrl) else {
    print("❌ Failed to open PDF: \(pdfPath)")
    exit(1)
}

let fileManager = FileManager.default
try? fileManager.createDirectory(atPath: outputDir, withIntermediateDirectories: true)

let pageCount = doc.pageCount
print("📄 Processing PDF: \(pdfPath) (\(pageCount) pages)")

for i in 0..<pageCount {
    guard let page = doc.page(at: i) else { continue }
    let pageBounds = page.bounds(for: .mediaBox)
    
    // Render at 3x resolution (~300 DPI)
    let scale: CGFloat = 3.0
    let targetSize = CGSize(width: pageBounds.width * scale, height: pageBounds.height * scale)
    
    let image = NSImage(size: targetSize)
    image.lockFocus()
    
    guard let context = NSGraphicsContext.current?.cgContext else {
        image.unlockFocus()
        continue
    }
    
    context.setFillColor(NSColor.white.cgColor)
    context.fill(CGRect(origin: .zero, size: targetSize))
    context.scaleBy(x: scale, y: scale)
    
    page.draw(with: .mediaBox, to: context)
    image.unlockFocus()
    
    guard let tiffData = image.tiffRepresentation,
          let bitmap = NSBitmapImageRep(data: tiffData),
          let pngData = bitmap.representation(using: .png, properties: [:]) else {
        print("❌ Failed to create PNG for page \(i+1)")
        continue
    }
    
    let baseName = prefix.isEmpty ? pdfUrl.deletingPathExtension().lastPathComponent : prefix
    let outFileName = "\(baseName)_p\(i+1).png"
    let outUrl = URL(fileURLWithPath: outputDir).appendingPathComponent(outFileName)
    
    do {
        try pngData.write(to: outUrl)
        print("  ✅ Rendered 300 DPI Image: \(outFileName)")
    } catch {
        print("❌ Failed to write \(outFileName): \(error)")
    }
}
