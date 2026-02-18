//
//  ActivityService.swift
//  EnlikoTrading
//
//  Cross-platform activity sync service
//

import Foundation
import Combine

// MARK: - Activity Models
struct ActivityItem: Codable, Identifiable {
    private let _id: Int?
    private let _actionType: String?
    private let _actionCategory: String?
    private let _source: String?
    let entityType: String?
    let oldValue: String?
    let newValue: String?
    private let _createdAt: String?
    
    var id: Int { _id ?? 0 }
    var actionType: String { _actionType ?? "unknown" }
    var actionCategory: String { _actionCategory ?? "general" }
    var source: String { _source ?? "unknown" }
    var createdAt: String { _createdAt ?? "" }
    
    enum CodingKeys: String, CodingKey {
        case _id = "id"
        case _actionType = "action_type"
        case _actionCategory = "action_category"
        case _source = "source"
        case entityType = "entity_type"
        case oldValue = "old_value"
        case newValue = "new_value"
        case _createdAt = "created_at"
    }
    
    var icon: String {
        switch actionCategory {
        case "settings":
            return "⚙️"
        case "trading":
            return "📊"
        case "auth":
            return "🔐"
        case "exchange":
            return "🔄"
        default:
            return "📝"
        }
    }
    
    var sourceIcon: String {
        switch source {
        case "ios":
            return "📱"
        case "webapp":
            return "🌐"
        case "telegram":
            return "💬"
        case "api":
            return "🔌"
        default:
            return "❓"
        }
    }
}

struct ActivityStats: Codable {
    let totalActivities: Int
    let bySource: [String: Int]
    let byCategory: [String: Int]
    let last24hCount: Int
    
    init(totalActivities: Int = 0, bySource: [String: Int] = [:], byCategory: [String: Int] = [:], last24hCount: Int = 0) {
        self.totalActivities = totalActivities
        self.bySource = bySource
        self.byCategory = byCategory
        self.last24hCount = last24hCount
    }
    
    enum CodingKeys: String, CodingKey {
        case totalActivities = "total_activities"
        case bySource = "by_source"
        case byCategory = "by_category"
        case last24hCount = "last_24h_count"
    }
}

struct SyncStatus: Codable {
    private let _pendingSync: Int?
    let lastSyncAt: String?
    private let _syncHealth: String?
    
    var pendingSync: Int { _pendingSync ?? 0 }
    var syncHealth: String { _syncHealth ?? "unknown" }
    
    enum CodingKeys: String, CodingKey {
        case _pendingSync = "pending_sync"
        case lastSyncAt = "last_sync_at"
        case _syncHealth = "sync_health"
    }
}

// MARK: - Activity Log Request
struct ActivityLogRequest: Codable {
    let actionType: String
    let actionCategory: String
    let source: String
    var entityType: String?
    var oldValue: String?
    var newValue: String?
    
    enum CodingKeys: String, CodingKey {
        case actionType = "action_type"
        case actionCategory = "action_category"
        case source
        case entityType = "entity_type"
        case oldValue = "old_value"
        case newValue = "new_value"
    }
}

// MARK: - Backend Response Structs (match actual backend format)

/// Backend /activity/history returns: {"success": true, "activities": [...], "count": N, "filters": {...}}
private struct ActivityHistoryResponse: Codable {
    let success: Bool?
    let activities: [ActivityItem]?
    let count: Int?
}

/// Backend /activity/recent returns: {"success": true, "activities": [...]}
private struct ActivityRecentResponse: Codable {
    let success: Bool?
    let activities: [ActivityItem]?
}

/// Backend /activity/stats returns: {"success": true, "period_days": N, "stats": {...}}
private struct ActivityStatsServerResponse: Codable {
    let success: Bool?
    let periodDays: Int?
    let stats: ActivityStatsData?
    
    enum CodingKeys: String, CodingKey {
        case success
        case periodDays = "period_days"
        case stats
    }
}

/// Stats data from backend
private struct ActivityStatsData: Codable {
    let totalActivities: Int?
    let bySource: [String: Int]?
    let byType: [String: Int]?
    let byDay: [String: Int]?
    
    enum CodingKeys: String, CodingKey {
        case totalActivities = "total_activities"
        case bySource = "by_source"
        case byType = "by_type"
        case byDay = "by_day"
    }
}

/// Backend /activity/trigger-sync returns: {"success": true, "message": "..."}
private struct TriggerSyncResponse: Codable {
    let success: Bool?
    let message: String?
}

// MARK: - Activity Service
@MainActor
class ActivityService: ObservableObject {
    static let shared = ActivityService()
    
    @Published var activities: [ActivityItem] = []
    @Published var recentActivities: [ActivityItem] = []
    @Published var stats: ActivityStats?
    @Published var syncStatus: SyncStatus?
    @Published var isLoading = false
    
    private let network = NetworkService.shared
    
    private init() {}
    
    // MARK: - Fetch Activity History
    @MainActor
    func fetchHistory(limit: Int = 50, source: String? = nil, category: String? = nil) async {
        isLoading = true
        defer { isLoading = false }
        
        var params: [String: String] = ["limit": String(limit)]
        if let source = source { params["source"] = source }
        if let category = category { params["category"] = category }
        
        do {
            // Backend returns {"success": true, "activities": [...]} — NOT data wrapper
            let response: ActivityHistoryResponse = try await network.get(
                Config.Endpoints.activityHistory,
                params: params
            )
            
            if let items = response.activities {
                self.activities = items
            }
        } catch {
            print("Failed to fetch activity history: \(error)")
        }
    }
    
    // MARK: - Fetch Recent Activities
    @MainActor
    func fetchRecent() async {
        do {
            // Backend returns {"success": true, "activities": [...]}
            let response: ActivityRecentResponse = try await network.get(
                Config.Endpoints.activityRecent
            )
            
            if let items = response.activities {
                self.recentActivities = items
            }
        } catch {
            print("Failed to fetch recent activities: \(error)")
        }
    }
    
    // MARK: - Fetch Activity Stats
    @MainActor
    func fetchStats() async {
        do {
            // Backend returns {"success": true, "stats": {...}}
            let response: ActivityStatsServerResponse = try await network.get(
                Config.Endpoints.activityStats
            )
            
            if let data = response.stats {
                // Map to our ActivityStats model
                self.stats = ActivityStats(
                    totalActivities: data.totalActivities ?? 0,
                    bySource: data.bySource ?? [:],
                    byCategory: data.byType ?? [:],
                    last24hCount: 0
                )
            }
        } catch {
            print("Failed to fetch activity stats: \(error)")
        }
    }
    
    // MARK: - Trigger Sync
    @MainActor
    func triggerSync() async -> Bool {
        do {
            // Backend returns {"success": true, "message": "..."} — no SyncStatus wrapper
            let response: TriggerSyncResponse = try await network.post(
                Config.Endpoints.activityTriggerSync,
                body: ["source": "ios"]
            )
            
            return response.success == true
        } catch {
            print("Failed to trigger sync: \(error)")
            return false
        }
    }
    
    // MARK: - Log Activity (local to server)
    func logActivity(
        actionType: String,
        category: String,
        entityType: String? = nil,
        oldValue: String? = nil,
        newValue: String? = nil
    ) async {
        do {
            var request = ActivityLogRequest(
                actionType: actionType,
                actionCategory: category,
                source: "ios"
            )
            request.entityType = entityType
            request.oldValue = oldValue
            request.newValue = newValue
            
            let _: SimpleResponse = try await network.post(
                Config.Endpoints.activityHistory,
                body: request
            )
        } catch {
            print("Failed to log activity: \(error)")
        }
    }
    
    // MARK: - Refresh All
    @MainActor
    func refreshAll() async {
        async let fetchRecent: () = fetchRecent()
        async let fetchStats: () = fetchStats()
        _ = await (fetchRecent, fetchStats)
    }
}
