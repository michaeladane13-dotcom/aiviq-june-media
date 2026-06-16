// add_reminder — create/delete Apple Reminders via EventKit (syncs to iPhone via iCloud).
// Built for macOS 14+ where the Reminders AppleScript bridge hangs. No AppleScript used.
//
// Usage:
//   add_reminder add "<title>" ["YYYY-MM-DD HH:MM"] ["notes"]   # create (optional due date + alarm)
//   add_reminder cleanup-test                                    # delete reminders titled __triage_test__*
import EventKit
import Foundation

let store = EKEventStore()

func grantAccess() -> Bool {
    let sema = DispatchSemaphore(value: 0)
    var ok = false
    if #available(macOS 14.0, *) {
        store.requestFullAccessToReminders { granted, _ in ok = granted; sema.signal() }
    } else {
        store.requestAccess(to: .reminder) { granted, _ in ok = granted; sema.signal() }
    }
    sema.wait()
    return ok
}

func err(_ s: String) { FileHandle.standardError.write((s + "\n").data(using: .utf8)!) }

let args = CommandLine.arguments
guard args.count >= 2 else {
    print("usage: add_reminder add \"<title>\" [\"YYYY-MM-DD HH:MM\"] [\"notes\"]  |  add_reminder cleanup-test")
    exit(1)
}

guard grantAccess() else { err("DENIED: no Reminders access (grant it in System Settings > Privacy & Security > Reminders)"); exit(2) }

switch args[1] {
case "add":
    guard args.count >= 3, !args[2].isEmpty else { err("ERROR: title required"); exit(1) }
    let r = EKReminder(eventStore: store)
    r.title = args[2]
    r.calendar = store.defaultCalendarForNewReminders()
    if args.count >= 4, !args[3].isEmpty {
        let df = DateFormatter()
        df.dateFormat = "yyyy-MM-dd HH:mm"
        df.timeZone = TimeZone.current
        if let d = df.date(from: args[3]) {
            r.dueDateComponents = Calendar.current.dateComponents([.year,.month,.day,.hour,.minute], from: d)
            r.addAlarm(EKAlarm(absoluteDate: d))   // fires a notification on the iPhone
        } else { err("WARN: could not parse date '\(args[3])' (want 'YYYY-MM-DD HH:MM'); created with no due date") }
    }
    if args.count >= 5, !args[4].isEmpty { r.notes = args[4] }
    do { try store.save(r, commit: true); print("OK: created reminder '\(r.title!)'" + (r.dueDateComponents != nil ? " (due set + alarm)" : "")) }
    catch { err("ERROR saving: \(error)"); exit(3) }

case "cleanup-test":
    let pred = store.predicateForReminders(in: nil)
    let sema = DispatchSemaphore(value: 0)
    var deleted = 0
    store.fetchReminders(matching: pred) { reminders in
        for r in (reminders ?? []) where (r.title ?? "").hasPrefix("__triage_test__") {
            try? store.remove(r, commit: false); deleted += 1
        }
        try? store.commit()
        sema.signal()
    }
    sema.wait()
    print("OK: deleted \(deleted) test reminder(s)")

default:
    err("unknown mode '\(args[1])' (use 'add' or 'cleanup-test')"); exit(1)
}
