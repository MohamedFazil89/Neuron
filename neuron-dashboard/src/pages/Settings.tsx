import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Settings as SettingsIcon, Shield, Bot, Folder, Bell } from 'lucide-react';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

const Settings = () => {
  return (
    <DashboardLayout>
      <div className="space-y-6 max-w-2xl">
        {/* Header */}
        <div>
          <div className="flex items-center gap-3">
            <SettingsIcon className="w-6 h-6 text-primary" />
            <h1 className="text-2xl font-bold">Settings</h1>
          </div>
          <p className="text-muted-foreground mt-1">
            Configure Neuron behavior and safety controls
          </p>
        </div>

        {/* Agent Configuration */}
        <div className="p-6 rounded-xl bg-card border border-border space-y-4">
          <div className="flex items-center gap-2 mb-4">
            <Bot className="w-5 h-5 text-muted-foreground" />
            <h2 className="font-semibold">Agent Configuration</h2>
          </div>

          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <Label>Default Model</Label>
                <p className="text-xs text-muted-foreground">Model used by agents</p>
              </div>
              <Select defaultValue="gpt-4">
                <SelectTrigger className="w-48">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="gpt-4">GPT-4 Turbo</SelectItem>
                  <SelectItem value="gpt-3.5">GPT-3.5 Turbo</SelectItem>
                  <SelectItem value="claude-3">Claude 3 Opus</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <Label>Verbosity Level</Label>
                <p className="text-xs text-muted-foreground">Log detail level</p>
              </div>
              <Select defaultValue="normal">
                <SelectTrigger className="w-48">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="quiet">Quiet</SelectItem>
                  <SelectItem value="normal">Normal</SelectItem>
                  <SelectItem value="verbose">Verbose</SelectItem>
                  <SelectItem value="debug">Debug</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <Label>Max Token Limit</Label>
                <p className="text-xs text-muted-foreground">Per task limit</p>
              </div>
              <Input type="number" defaultValue={50000} className="w-48" />
            </div>
          </div>
        </div>

        {/* Safety Controls */}
        <div className="p-6 rounded-xl bg-card border border-border space-y-4">
          <div className="flex items-center gap-2 mb-4">
            <Shield className="w-5 h-5 text-muted-foreground" />
            <h2 className="font-semibold">Safety Controls</h2>
          </div>

          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <Label>Dry Run Mode</Label>
                <p className="text-xs text-muted-foreground">Preview changes without applying</p>
              </div>
              <Switch />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <Label>Read-Only Mode</Label>
                <p className="text-xs text-muted-foreground">Prevent all file modifications</p>
              </div>
              <Switch />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <Label>Auto-Patching</Label>
                <p className="text-xs text-muted-foreground">Apply patches automatically</p>
              </div>
              <Switch defaultChecked />
            </div>
          </div>
        </div>

        {/* Workspace */}
        <div className="p-6 rounded-xl bg-card border border-border space-y-4">
          <div className="flex items-center gap-2 mb-4">
            <Folder className="w-5 h-5 text-muted-foreground" />
            <h2 className="font-semibold">Workspace</h2>
          </div>

          <div className="space-y-4">
            <div>
              <Label>Workspace Path</Label>
              <div className="flex gap-2 mt-2">
                <Input defaultValue="/tmp/neuron-workspace" className="flex-1" />
                <Button variant="secondary">Browse</Button>
              </div>
            </div>

            <Separator />

            <div>
              <Label>Protected Files</Label>
              <p className="text-xs text-muted-foreground mb-2">
                Files Neuron must never modify (one per line)
              </p>
              <textarea 
                className="w-full h-24 px-3 py-2 text-sm rounded-md border border-input bg-background font-mono"
                defaultValue={".env\npackage-lock.json\n*.key"}
              />
            </div>
          </div>
        </div>

        {/* Notifications */}
        <div className="p-6 rounded-xl bg-card border border-border space-y-4">
          <div className="flex items-center gap-2 mb-4">
            <Bell className="w-5 h-5 text-muted-foreground" />
            <h2 className="font-semibold">Notifications</h2>
          </div>

          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <Label>Task Completion</Label>
                <p className="text-xs text-muted-foreground">Notify when tasks complete</p>
              </div>
              <Switch defaultChecked />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <Label>Error Alerts</Label>
                <p className="text-xs text-muted-foreground">Notify on agent failures</p>
              </div>
              <Switch defaultChecked />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <Label>Telemetry</Label>
                <p className="text-xs text-muted-foreground">Send anonymous usage data</p>
              </div>
              <Switch />
            </div>
          </div>
        </div>

        <Button className="w-full">Save Settings</Button>
      </div>
    </DashboardLayout>
  );
};

export default Settings;
