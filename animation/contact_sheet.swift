// Render a labeled grid from JSON [{file, label, detail}], without adding dependencies.
import AppKit
let args=CommandLine.arguments
precondition(args.count==5,"contact_sheet.swift metadata.json output.png columns cellScale")
let metadata=URL(fileURLWithPath:args[1]), output=URL(fileURLWithPath:args[2])
let columns=Int(args[3])!, scale=Int(args[4])!
precondition(columns>0 && scale>0)
let items=try JSONSerialization.jsonObject(with:Data(contentsOf:metadata)) as! [[String:String]]
precondition(!items.isEmpty)
let rows=(items.count+columns-1)/columns, gap=8, cellW=240*scale, cellH=280*scale+40
let width=columns*(cellW+gap)+gap, height=rows*(cellH+gap)+gap
let bitmap=NSBitmapImageRep(bitmapDataPlanes:nil,pixelsWide:width,pixelsHigh:height,bitsPerSample:8,samplesPerPixel:4,hasAlpha:true,isPlanar:false,colorSpaceName:.deviceRGB,bytesPerRow:0,bitsPerPixel:0)!
NSGraphicsContext.saveGraphicsState();NSGraphicsContext.current=NSGraphicsContext(bitmapImageRep:bitmap)
NSColor(calibratedWhite:0.12,alpha:1).setFill();NSRect(x:0,y:0,width:width,height:height).fill()
NSGraphicsContext.current!.imageInterpolation = .none
for (i,item) in items.enumerated() {
    let image=NSImage(contentsOfFile:item["file"]!)!
    let x=gap+(i%columns)*(cellW+gap), y=height-gap-(i/columns+1)*(cellH+gap)
    image.draw(in:NSRect(x:x,y:y,width:cellW,height:280*scale))
    let text="\(item["label"]!)  \(item["detail"] ?? "")"
    (text as NSString).draw(at:NSPoint(x:x+8,y:y+280*scale+8),withAttributes:[.font:NSFont.systemFont(ofSize:20,weight:.semibold),.foregroundColor:NSColor.white])
}
NSGraphicsContext.restoreGraphicsState()
try bitmap.representation(using:.png,properties:[:])!.write(to:output)
precondition(FileManager.default.fileExists(atPath:output.path))
print(output.path)
