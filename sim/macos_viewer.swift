// Native Retina viewer: keep the source pixels until CoreGraphics renders them.
import AppKit

func panelSize(width: Int, height: Int, widthMM: Double, ppi: Double, scale: Double) -> NSSize {
    let points = scale > 0 ? Double(width) * scale : widthMM / 25.4 * ppi
    return NSSize(width: points, height: points * Double(height) / Double(width))
}

final class PanelView: NSView {
    var image: CGImage?

    override func draw(_ dirtyRect: NSRect) {
        NSColor.black.setFill()
        bounds.fill()
        guard let image = image, let context = NSGraphicsContext.current?.cgContext else { return }
        context.interpolationQuality = .none
        context.draw(image, in: bounds)
    }
}

final class Viewer: NSObject, NSApplicationDelegate, NSWindowDelegate {
    let width = Int(CommandLine.arguments[1])!
    let height = Int(CommandLine.arguments[2])!
    let widthMM = Double(CommandLine.arguments[3])!
    let overridePPI = Double(CommandLine.arguments[4])!
    let scale = Double(CommandLine.arguments[5])!
    let panel = PanelView()
    let status = NSTextField(labelWithString: "")
    var window: NSWindow!

    func applicationDidFinishLaunching(_ notification: Notification) {
        let screen = NSScreen.screens.first { screen in
            let id = screen.deviceDescription[NSDeviceDescriptionKey("NSScreenNumber")] as! CGDirectDisplayID
            return CGDisplayIsBuiltin(id) != 0
        } ?? NSScreen.main!
        window = NSWindow(contentRect: .zero, styleMask: [.titled, .closable, .miniaturizable],
                          backing: .buffered, defer: false, screen: screen)
        window.title = "MacDesk Buddy · 240×280"
        window.delegate = self
        window.contentView!.addSubview(panel)
        window.contentView!.addSubview(status)
        resize(for: screen)
        window.center()
        window.makeKeyAndOrderFront(nil)
        NSApp.activate(ignoringOtherApps: true)

        DispatchQueue.global(qos: .userInteractive).async { self.readFrames() }
    }

    func resize(for screen: NSScreen) {
        let id = screen.deviceDescription[NSDeviceDescriptionKey("NSScreenNumber")] as! CGDirectDisplayID
        let mm = CGDisplayScreenSize(id).width
        guard scale > 0 || overridePPI > 0 || mm > 0 else {
            fputs("Cannot determine display size; supply --ppi after ruler calibration.\n", stderr)
            exit(2)
        }
        let ppi = overridePPI > 0 ? overridePPI : (mm > 0 ? screen.frame.width / mm * 25.4 : 0)
        let size = panelSize(width: width, height: height, widthMM: widthMM, ppi: ppi, scale: scale)
        // The status strip and title bar are outside the measured display area.
        window.setContentSize(NSSize(width: size.width, height: size.height + 28))
        panel.frame = NSRect(origin: NSPoint(x: 0, y: 28), size: size)
        status.frame = NSRect(x: 4, y: 2, width: size.width - 8, height: 24)
        status.font = .monospacedSystemFont(ofSize: 10, weight: .regular)
        status.stringValue = scale > 0 ? "240×280 · ×\(scale)" : String(format: "%.2f × %.2f mm", widthMM, widthMM * Double(height) / Double(width))
        print(String(format: "preview: %dx%d source, %.3fx%.3f points, %.3f pt/in, %.1fx backing", width, height, size.width, size.height, ppi, screen.backingScaleFactor))
        fflush(stdout)
    }

    func windowDidChangeScreen(_ notification: Notification) {
        if let screen = window.screen { resize(for: screen) }
    }

    func windowDidChangeBackingProperties(_ notification: Notification) {
        if let screen = window.screen { resize(for: screen) }
    }

    func windowWillClose(_ notification: Notification) { NSApp.terminate(nil) }

    func readFrames() {
        let frameBytes = width * height * 3
        var renderedFrames = 0
        while true {
            var data = Data()
            while data.count < frameBytes {
                let chunk = FileHandle.standardInput.readData(ofLength: frameBytes - data.count)
                if chunk.isEmpty {
                    if !data.isEmpty { fputs("Incomplete simulator frame.\n", stderr) }
                    print("viewer: rendered \(renderedFrames) frame(s)")
                    fflush(stdout)
                    DispatchQueue.main.async { NSApp.terminate(nil) }
                    return
                }
                data.append(chunk)
            }
            guard let provider = CGDataProvider(data: data as CFData),
                  let image = CGImage(width: width, height: height, bitsPerComponent: 8,
                      bitsPerPixel: 24, bytesPerRow: width * 3,
                      space: CGColorSpaceCreateDeviceRGB(), bitmapInfo: CGBitmapInfo(rawValue: 0),
                      provider: provider, decode: nil, shouldInterpolate: false, intent: .defaultIntent)
            else { fatalError("Cannot create simulator frame") }
            // Backpressure keeps old frames from accumulating in the UI queue.
            DispatchQueue.main.sync {
                self.panel.image = image
                self.panel.needsDisplay = true
                self.panel.displayIfNeeded()
            }
            renderedFrames += 1
        }
    }
}

if CommandLine.arguments.dropFirst() == ["--self-test"] {
    for ppi in [127.0, 151.5, 100.0] {
        let size = panelSize(width: 240, height: 280, widthMM: 27.972, ppi: ppi, scale: 0)
        assert(abs(size.width / ppi * 25.4 - 27.972) < 1e-9)
        assert(abs(size.height / ppi * 25.4 - 32.634) < 1e-9)
        assert(abs(size.width / size.height - 240.0 / 280.0) < 1e-9)
    }
    assert(panelSize(width: 240, height: 280, widthMM: 27.972, ppi: 151.5, scale: 1)
           == NSSize(width: 240, height: 280))
    print("Physical size and aspect-ratio checks passed.")
} else {
    let app = NSApplication.shared
    app.setActivationPolicy(.regular)
    let viewer = Viewer()
    app.delegate = viewer
    app.run()
}
