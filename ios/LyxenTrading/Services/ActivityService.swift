//
//  ActivityService.swift
//  LyxenTrading
//
//  Cross-platform activity sync service
//

import Foundation
import Combine

// MARK: - Activity Models
struct ActivityItem: Codable, Identifiable {
    let id: Int
    let actionType: String
    let actionCategory: String
    let source: String        // "ios", "webapp", "telegram", "api"
    let entityType: String?
    let oldValue: String?
    let newValue: String?
    let createdAt: String
    
    enum CodingKeys: String, CodingKey {
        case id
        case actionType = "action_type"
        case actionCategory = "action_category"
        case source
        case entityType = "entity_type"
        case oldValue = "old_value"
        case newValue = "new_value"
        case createdAt = "created_at"
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
    
    enum CodingKeys: String, CodingKey {
        case totalActivities = "total_activities"
        case bySource = "by_source"
        case byCategory = "by_category"
        case last24hCount = "last_24h_count"
    }
}

struct SyncStatus: Codable {
    let pendingSync: Int
    let lastSyncAt: String?
    let syncHealth: String  // "healthy", "delayed", "error"
    
    enum CodingKeys: String, CodingKey {
        case pendingSync = "pending_sync"
        case lastSyncAt = "last_sync_at"
        case syncHealth = "sync_health"
    }
}

// MARK: - Activity Service
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
            let response: APIResponse<[ActivityItem]> = try await network.get(
                Config.Endpoints.activityHistory,
                params: params
            )
            
            if let data = response.data {
                self.activities = data
            }
        } catch {
            print("Failed to fetch activity history: \(error)")
        }
    }
    
    // MARK: - Fetch Recent Activities
    @MainActor
    func fetchRecent() async {
        do {
            let response: APIResponse<[ActivityItem]> = try await network.get(
                Config.Endpoints.activityRecent
            )
            
            if let data = response.data {
                self.recentActivities = data
            }
        } catch {
            print("Failed to fetch recent activities: \(error)")
        }
    }
    
    // MARK: - Fetch Activity Stats
    @MainActor
    func fetchStats() async {
        do {
            let response: APIResponse<ActivityStats> = try await network.get(
                Config.Endpoints.activityStats
            )
            
            if let data = response.data {
                self.stats = data
            }
        } catch {
            print("Failed to fetch activity stats: \(error)")
        }
    }
    
    // MARK: - Trigger Sync
    @MainActor
    func triggerSync() async -> Bool {
        do {
            let response: APIResponse<SyncStatus> = try await network.post(
                Config.Endpoints.activityTriggerSync,
                body: ["source": "ios"]
            )
            
            if let status = response.data {
                self.syncStatus = status
                return true
            }
            return false
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
            var body: [String: Any] = [
                "action_type": actionType,
                "action_category": category,
                "source": "ios"
            ]
            if let entityType = entityType { body["entity_type"] = entityType }
            if let oldValue = oldValue { body["old_value"] = oldValue }
            if let newValue = newValue { body["new_value"] = newValue }
            
            let _: APIResponse<EmptyResponse> = try await network.post(
                Config.Endpoints.activityHistory,
                body: body
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
