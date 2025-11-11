import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-prompt-dictionary-viewer',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './prompt-dictionary-viewer.html',
  styleUrls: ['./prompt-dictionary-viewer.css']
})
export class PromptDictionaryViewer {
  @Input() dictionary: Record<string, string> | null | undefined = null;
  @Input() title: string = 'Translation Dictionary';
  
  expanded = false;

  get entries(): Array<{key: string, value: string}> {
    if (!this.dictionary) return [];
    return Object.entries(this.dictionary).map(([key, value]) => ({ key, value }));
  }

  get hasEntries(): boolean {
    return this.entries.length > 0;
  }

  toggleExpanded(): void {
    this.expanded = !this.expanded;
  }
}
