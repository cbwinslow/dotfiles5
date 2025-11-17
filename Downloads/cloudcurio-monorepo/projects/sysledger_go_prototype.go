// =============================================================
// Project: sysledger (System Configuration Ledger Prototype)
// Date:    2025-11-16
// Author:  ChatGPT (for cbwinslow / cloudcurio)
// Summary: Cross-platform Go CLI skeleton for tracking system
//          configuration changes and exporting a declarative
//          manifest ("Configuration as Code").
//
// NOTE: This single text document contains all project files.
//       Each file is prefixed with a marker: `// FILE: <path>`.
//       You can split them into real files in a repo.
// =============================================================

// FILE: go.mod
module github.com/cbwinslow/sysledger

go 1.22

require (
	github.com/fsnotify/fsnotify v1.7.0
	github.com/spf13/cobra v1.8.0
)


// FILE: cmd/sysledger/main.go
package main

// =============================================================
// File:    cmd/sysledger/main.go
// Date:    2025-11-16
// Author:  ChatGPT for cbwinslow
// Summary: Entry point for the sysledger CLI application.
// Inputs:  Command-line arguments (via os.Args).
// Outputs: Exit code (0 on success, non-zero on error).
// Notes:   Delegates all logic to the internal/cli package.
// Mod Log: 2025-11-16 - Initial version.
// =============================================================

import "github.com/cbwinslow/sysledger/internal/cli"

func main() {
	cli.Execute()
}


// FILE: internal/cli/root.go
package cli

import (
	"fmt"
	"os"

	"github.com/spf13/cobra"
)

// =============================================================
// File:    internal/cli/root.go
// Date:    2025-11-16
// Author:  ChatGPT for cbwinslow
// Summary: Defines the root Cobra command and CLI bootstrap.
// Inputs:  Subcommands and flags registered at init time.
// Outputs: User-facing CLI behavior and exit codes.
// Mod Log: 2025-11-16 - Initial version.
// =============================================================

// rootCmd is the base command for the sysledger CLI.
var rootCmd = &cobra.Command{
	Use:   "sysledger",
	Short: "System configuration ledger and replay tool",
	Long: `sysledger tracks configuration changes on your system,
records them as a timeline, and can export a declarative
"Configuration as Code" manifest to rebuild or audit your environment.`,
}

// Execute runs the root command and returns an appropriate exit code.
func Execute() {
	if err := rootCmd.Execute(); err != nil {
		// Print the error for the user and exit with non-zero status.
		fmt.Fprintln(os.Stderr, "error:", err)
		os.Exit(1)
	}
}

func init() {
	// Register subcommands here.
	rootCmd.AddCommand(watchCmd)
	rootCmd.AddCommand(snapshotCmd)
	rootCmd.AddCommand(exportCmd)
}


// FILE: internal/cli/watch.go
package cli

import (
	"context"
	"fmt"
	"time"

	"github.com/cbwinslow/sysledger/internal/watcher"
	"github.com/spf13/cobra"
)

// =============================================================
// File:    internal/cli/watch.go
// Date:    2025-11-16
// Author:  ChatGPT for cbwinslow
// Summary: Implements the `sysledger watch` command, which starts
//          a long-running process to monitor tracked directories
//          for changes and record them as events.
// Inputs:  Optional flags: --path, --debounce, --once.
// Outputs: Logs to stdout/stderr and event records on disk.
// Mod Log: 2025-11-16 - Initial version.
// =============================================================

var (
	watchPath    string
	watchDebounce time.Duration
	watchOnce    bool
)

// watchCmd defines the CLI interface for continuous file watching.
var watchCmd = &cobra.Command{
	Use:   "watch",
	Short: "Watch tracked directories for configuration changes",
	RunE: func(cmd *cobra.Command, args []string) error {
		ctx := context.Background()

		cfg := watcher.Config{
			RootPath: watchPath,
			Debounce: watchDebounce,
			Once:     watchOnce,
		}

		fmt.Println("[sysledger] starting watcher on", cfg.RootPath)
		return watcher.Run(ctx, cfg)
	},
}

func init() {
	watchCmd.Flags().StringVarP(&watchPath, "path", "p", "$HOME", "Root path to watch (default: $HOME)")
	watchCmd.Flags().DurationVar(&watchDebounce, "debounce", 2*time.Second, "Debounce interval for batching rapid changes")
	watchCmd.Flags().BoolVar(&watchOnce, "once", false, "Run a single scan and exit instead of long-running watch")
}


// FILE: internal/cli/snapshot.go
package cli

import (
	"fmt"

	"github.com/cbwinslow/sysledger/internal/storage"
	"github.com/spf13/cobra"
)

// =============================================================
// File:    internal/cli/snapshot.go
// Date:    2025-11-16
// Author:  ChatGPT for cbwinslow
// Summary: Implements the `sysledger snapshot` command, which
//          records a point-in-time snapshot of tracked configuration
//          files without starting a long-running watcher.
// Inputs:  Optional flags: --path, --tag.
// Outputs: Snapshot metadata written to the storage backend.
// Mod Log: 2025-11-16 - Initial version.
// =============================================================

var (
	snapshotPath string
	snapshotTag  string
)

// snapshotCmd defines a one-shot snapshot command.
var snapshotCmd = &cobra.Command{
	Use:   "snapshot",
	Short: "Take an immediate snapshot of configuration state",
	RunE: func(cmd *cobra.Command, args []string) error {
		backend := storage.DefaultBackend()
		meta, err := backend.CreateSnapshot(snapshotPath, snapshotTag)
		if err != nil {
			return err
		}
		fmt.Printf("[sysledger] snapshot created: id=%s tag=%s\n", meta.ID, meta.Tag)
		return nil
	},
}

func init() {
	snapshotCmd.Flags().StringVarP(&snapshotPath, "path", "p", "$HOME", "Root path to snapshot (default: $HOME)")
	snapshotCmd.Flags().StringVarP(&snapshotTag, "tag", "t", "", "Optional human-readable tag for this snapshot")
}


// FILE: internal/cli/export.go
package cli

import (
	"fmt"
	"os"

	"github.com/cbwinslow/sysledger/internal/manifest"
	"github.com/cbwinslow/sysledger/internal/storage"
	"github.com/spf13/cobra"
)

// =============================================================
// File:    internal/cli/export.go
// Date:    2025-11-16
// Author:  ChatGPT for cbwinslow
// Summary: Implements the `sysledger export` command, which
//          transforms snapshot data into a declarative manifest
//          and emits it as YAML or JSON.
// Inputs:  Flags: --snapshot-id, --format.
// Outputs: Manifest to stdout.
// Mod Log: 2025-11-16 - Initial version.
// =============================================================

var (
	exportSnapshotID string
	exportFormat     string
)

// exportCmd defines the command that emits a CaC manifest.
var exportCmd = &cobra.Command{
	Use:   "export",
	Short: "Export a Configuration-as-Code manifest from a snapshot",
	RunE: func(cmd *cobra.Command, args []string) error {
		backend := storage.DefaultBackend()

		// Resolve snapshot ID: if none provided, use the latest.
		meta, err := backend.ResolveSnapshot(exportSnapshotID)
		if err != nil {
			return err
		}

		// Build a manifest from the snapshot contents.
		m, err := manifest.FromSnapshot(meta)
		if err != nil {
			return err
		}

		// Encode the manifest in the requested format.
		var encoded []byte
		switch exportFormat {
		case "yaml", "yml", "":
			encoded, err = m.MarshalYAML()
		case "json":
			encoded, err = m.MarshalJSON()
		default:
			return fmt.Errorf("unsupported export format: %s", exportFormat)
		}
		if err != nil {
			return err
		}

		// Write manifest to stdout.
		if _, err := os.Stdout.Write(encoded); err != nil {
			return err
		}
		// Ensure a trailing newline for convenience.
		fmt.Println()
		return nil
	},
}

func init() {
	exportCmd.Flags().StringVarP(&exportSnapshotID, "snapshot-id", "s", "", "Snapshot ID to export (default: latest)")
	exportCmd.Flags().StringVarP(&exportFormat, "format", "f", "yaml", "Output format: yaml or json")
}


// FILE: internal/watcher/watcher.go
package watcher

import (
	"context"
	"fmt"
	"os"
	"path/filepath"
	"time"

	"github.com/fsnotify/fsnotify"
)

// =============================================================
// File:    internal/watcher/watcher.go
// Date:    2025-11-16
// Author:  ChatGPT for cbwinslow
// Summary: Provides a simple filesystem watcher abstraction using
//          fsnotify. In a full implementation, this would batch
//          events, classify them, and forward them into storage.
// Inputs:  Config specifying root path, debounce interval, etc.
// Outputs: Logs and (eventually) structured change records.
// Mod Log: 2025-11-16 - Initial version (stub behavior).
// =============================================================

// Config holds runtime parameters for the watcher.
type Config struct {
	// RootPath is the directory tree to watch. It may contain
	// environment variables such as $HOME, which will be expanded.
	RootPath string

	// Debounce controls how often rapid events are batched together.
	Debounce time.Duration

	// Once, when true, performs a single scan and exits instead of
	// running as a long-lived watcher. This is useful for testing.
	Once bool
}

// Run starts the watcher using the provided configuration and a
// context for cancellation. For now, this implementation is a stub
// that demonstrates basic fsnotify usage and logs events.
func Run(ctx context.Context, cfg Config) error {
	// Expand environment variables in RootPath (e.g., $HOME).
	root := os.ExpandEnv(cfg.RootPath)

	info, err := os.Stat(root)
	if err != nil {
		return fmt.Errorf("unable to stat root path %s: %w", root, err)
	}
	if !info.IsDir() {
		return fmt.Errorf("root path is not a directory: %s", root)
	}

	watcher, err := fsnotify.NewWatcher()
	if err != nil {
		return fmt.Errorf("failed to create watcher: %w", err)
	}
	defer watcher.Close()

	// Helper to recursively add directories.
	addDir := func(path string) error {
		return filepath.WalkDir(path, func(p string, d os.DirEntry, walkErr error) error {
			if walkErr != nil {
				// Log and continue rather than failing the entire walk.
				fmt.Fprintf(os.Stderr, "[sysledger] warn: walk error on %s: %v\n", p, walkErr)
				return nil
			}
			if d.IsDir() {
				if err := watcher.Add(p); err != nil {
					fmt.Fprintf(os.Stderr, "[sysledger] warn: cannot watch %s: %v\n", p, err)
				}
			}
			return nil
		})
	}

	if err := addDir(root); err != nil {
		return fmt.Errorf("failed to add directories for watch: %w", err)
	}

	fmt.Println("[sysledger] watcher initialized for", root)

	// Basic event loop. In a production version, you would:
	// - debounce events
	// - classify changes
	// - write structured events into a storage backend.
	for {
		select {
		case <-ctx.Done():
			return ctx.Err()
		case event, ok := <-watcher.Events:
			if !ok {
				return nil
			}
			fmt.Printf("[sysledger] event: %s %s\n", event.Op.String(), event.Name)
		case err, ok := <-watcher.Errors:
			if !ok {
				return nil
			}
			fmt.Fprintf(os.Stderr, "[sysledger] watcher error: %v\n", err)
		}
	}
}


// FILE: internal/storage/storage.go
package storage

import (
	"fmt"
	"time"
)

// =============================================================
// File:    internal/storage/storage.go
// Date:    2025-11-16
// Author:  ChatGPT for cbwinslow
// Summary: Defines storage interfaces and a simple in-memory/
//          placeholder backend for snapshot metadata. In a full
//          implementation, this would be backed by SQLite, git, or
//          another durable store.
// Inputs:  Snapshot requests from CLI/Watcher.
// Outputs: Snapshot metadata and access helpers.
// Mod Log: 2025-11-16 - Initial version (stub backend).
// =============================================================

// SnapshotMeta captures basic information about a recorded snapshot.
type SnapshotMeta struct {
	ID        string    // Unique identifier for the snapshot
	Tag       string    // Optional human-friendly tag
	RootPath  string    // Root path that was snapshotted
	CreatedAt time.Time // Timestamp of snapshot creation
}

// Backend describes the minimal behavior expected from a storage
// implementation that can persist and retrieve snapshots.
type Backend interface {
	// CreateSnapshot records a new snapshot for the given root path
	// and optional tag. A full implementation would scan the file
	// tree and persist content hashes or diffs alongside metadata.
	CreateSnapshot(rootPath, tag string) (*SnapshotMeta, error)

	// ResolveSnapshot finds a snapshot by ID. If the ID is empty,
	// implementations may return the latest snapshot.
	ResolveSnapshot(id string) (*SnapshotMeta, error)
}

// defaultBackend is a process-local, in-memory backend used only
// for prototyping. It should be replaced with a durable backend.
var defaultBackend Backend = NewInMemoryBackend()

// DefaultBackend returns the globally configured storage backend.
func DefaultBackend() Backend {
	return defaultBackend
}

// SetDefaultBackend allows advanced users or tests to override the
// global backend implementation at runtime.
func SetDefaultBackend(b Backend) {
	defaultBackend = b
}

// ==================== In-memory backend =======================

// InMemoryBackend is a trivial, non-durable snapshot backend that
// stores metadata in process memory. This is useful for early
// development and unit tests, but not for real-world usage.
type InMemoryBackend struct {
	snapshots []*SnapshotMeta
}

// NewInMemoryBackend constructs a new empty in-memory backend.
func NewInMemoryBackend() *InMemoryBackend {
	return &InMemoryBackend{
		snapshots: make([]*SnapshotMeta, 0, 16),
	}
}

// CreateSnapshot inserts a new snapshot record in memory.
func (b *InMemoryBackend) CreateSnapshot(rootPath, tag string) (*SnapshotMeta, error) {
	if rootPath == "" {
		return nil, fmt.Errorf("rootPath must not be empty")
	}

	meta := &SnapshotMeta{
		ID:        fmt.Sprintf("snap-%d", time.Now().UnixNano()),
		Tag:       tag,
		RootPath:  rootPath,
		CreatedAt: time.Now().UTC(),
	}

	b.snapshots = append(b.snapshots, meta)
	return meta, nil
}

// ResolveSnapshot returns either the requested ID or the latest.
func (b *InMemoryBackend) ResolveSnapshot(id string) (*SnapshotMeta, error) {
	if len(b.snapshots) == 0 {
		return nil, fmt.Errorf("no snapshots available")
	}

	if id == "" {
		// Return the latest snapshot.
		return b.snapshots[len(b.snapshots)-1], nil
	}

	for _, s := range b.snapshots {
		if s.ID == id {
			return s, nil
		}
	}
	return nil, fmt.Errorf("snapshot not found: %s", id)
}


// FILE: internal/manifest/manifest.go
package manifest

import (
	"encoding/json"

	"gopkg.in/yaml.v3"

	"github.com/cbwinslow/sysledger/internal/storage"
)

// =============================================================
// File:    internal/manifest/manifest.go
// Date:    2025-11-16
// Author:  ChatGPT for cbwinslow
// Summary: Defines the high-level manifest structure that
//          represents the desired configuration state in a
//          declarative (Configuration-as-Code) format.
// Inputs:  Snapshot metadata and (eventually) snapshot content.
// Outputs: Serialized YAML/JSON manifest suitable for replay.
// Mod Log: 2025-11-16 - Initial version (metadata-only skeleton).
// =============================================================

// Manifest is a high-level, OS-agnostic description of a system's
// configuration. Over time this can grow to include packages,
// services, dotfiles, editors, desktop settings, and more.
type Manifest struct {
	// Metadata about how/when this manifest was generated.
	GeneratedAt string `json:"generated_at" yaml:"generated_at"`
	SourceID    string `json:"source_snapshot_id" yaml:"source_snapshot_id"`
	SourceTag   string `json:"source_snapshot_tag" yaml:"source_snapshot_tag"`

	// RootPath is the path that the snapshot and manifest describe.
	RootPath string `json:"root_path" yaml:"root_path"`

	// TODO: Expand this section over time to include real config:
	// Packages, dotfiles, services, editors, desktop config, etc.
}

// FromSnapshot builds a basic manifest from snapshot metadata. In a
// full implementation, this function would also inspect the actual
// file tree, parse configuration files, and infer higher-level
// semantics (packages, services, themes, etc.).
func FromSnapshot(meta *storage.SnapshotMeta) (*Manifest, error) {
	m := &Manifest{
		GeneratedAt: meta.CreatedAt.Format("2006-01-02T15:04:05Z07:00"),
		SourceID:    meta.ID,
		SourceTag:   meta.Tag,
		RootPath:    meta.RootPath,
	}
	return m, nil
}

// MarshalYAML encodes the manifest as YAML.
func (m *Manifest) MarshalYAML() ([]byte, error) {
	return yaml.Marshal(m)
}

// MarshalJSON encodes the manifest as JSON.
func (m *Manifest) MarshalJSON() ([]byte, error) {
	return json.MarshalIndent(m, "", "  ")
}


// FILE: README.md
// =============================================================
// Project: sysledger (Prototype)
// Date:    2025-11-16
// Author:  ChatGPT for cbwinslow / cloudcurio
// Summary: sysledger is an experimental tool that:
//          - Watches configuration directories for changes
//          - Records snapshots of the system state
//          - Exports a Configuration-as-Code manifest that can be
//            used to audit or reconstruct the environment.
//
// Status:  This is an early skeleton intended to establish a clean
//          Go project structure and CLI using Cobra. Core features
//          such as durable storage, rich manifest extraction, and
//          AI-assisted analysis are left as future enhancements.
//
// Quick start:
//
//   go mod tidy
//   go build ./cmd/sysledger
//   ./sysledger --help
//   ./sysledger snapshot --path "$HOME" --tag "initial"
//   ./sysledger export --format yaml
//
// Next steps / Improvements:
//   1. Replace the in-memory storage backend with a durable
//      implementation (SQLite or git-backed store).
//   2. Expand the manifest structure to include packages, dotfiles,
//      services, and editor/desktop configuration.
//   3. Integrate a robust watcher pipeline that debounces events,
//      classifies them, and persists structured change records.
//   4. Add tests, logging, and configuration via a YAML/TOML file.
//   5. Add an AI analysis layer to summarize diffs and propose
//      clean, minimal manifests and replay scripts.
// =============================================================
