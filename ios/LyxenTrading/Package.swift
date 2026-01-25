// swift-tools-version:5.9
// Package.swift
// LyxenTrading
//
// Swift Package Manager configuration for building outside Xcode
//

import PackageDescription

let package = Package(
    name: "LyxenTrading",
    platforms: [
        .iOS(.v16),
        .macOS(.v13)
    ],
    products: [
        .library(
            name: "LyxenTrading",
            targets: ["LyxenTrading"]
        )
    ],
    dependencies: [
        // No external dependencies - pure Swift/SwiftUI
    ],
    targets: [
        .target(
            name: "LyxenTrading",
            dependencies: [],
            path: ".",
            exclude: ["README.md", "Info.plist"],
            sources: [
                "App",
                "Models",
                "Services",
                "Views",
                "ViewModels",
                "Extensions",
                "Utils"
            ],
            resources: [
                .process("Resources")
            ]
        )
    ]
)
