import { Component, Input, Output, EventEmitter, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

interface DictionaryEntry {
  key: string;
  value: string;
}

@Component({
  selector: 'app-prompt-dictionary-editor',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './prompt-dictionary-editor.html',
  styleUrls: ['./prompt-dictionary-editor.css']
})
export class PromptDictionaryEditor implements OnInit {
  @Input() dictionary: Record<string, string> | null | undefined = null;
  @Output() dictionaryChange = new EventEmitter<Record<string, string> | null>();
  
  entries: DictionaryEntry[] = [];
  showHelp = false;
  private isInternalUpdate = false;

  ngOnInit(): void {
    this.loadDictionary();
  }

  ngOnChanges(): void {
    // Only reload if the change came from outside (not from our own emitChanges)
    if (!this.isInternalUpdate) {
      this.loadDictionary();
    }
    this.isInternalUpdate = false;
  }

  private loadDictionary(): void {
    if (this.dictionary) {
      this.entries = Object.entries(this.dictionary).map(([key, value]) => ({
        key,
        value
      }));
    } else {
      this.entries = [];
    }
    
    // Always ensure there's at least one empty entry for adding new terms
    if (this.entries.length === 0) {
      this.addEntry();
    }
  }

  addEntry(): void {
    this.entries.push({ key: '', value: '' });
  }

  removeEntry(index: number): void {
    this.entries.splice(index, 1);
    if (this.entries.length === 0) {
      this.addEntry();
    }
    this.emitChanges();
  }

  onEntryChange(): void {
    this.emitChanges();
  }

  private emitChanges(): void {
    this.isInternalUpdate = true;
    
    // Filter out empty entries
    const validEntries = this.entries.filter(e => e.key.trim() && e.value.trim());
    
    if (validEntries.length === 0) {
      this.dictionaryChange.emit(null);
      return;
    }

    // Convert to dictionary object
    const dictionary: Record<string, string> = {};
    validEntries.forEach(entry => {
      dictionary[entry.key.trim()] = entry.value.trim();
    });
    
    this.dictionaryChange.emit(dictionary);
  }

  toggleHelp(): void {
    this.showHelp = !this.showHelp;
  }

  loadExample(): void {
    this.entries = [
      { key: '김민준', value: 'Kim Min-jun' },
      { key: '불사 연맹', value: 'Immortal Alliance' },
      { key: '천계', value: 'Celestial Realm' },
      { key: '마나', value: 'Mana' },
      { key: '', value: '' }
    ];
    this.emitChanges();
  }

  clearAll(): void {
    this.entries = [{ key: '', value: '' }];
    this.emitChanges();
  }
}
