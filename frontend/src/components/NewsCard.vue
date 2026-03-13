<template>
  <a
    :href="news.link"
    target="_blank"
    rel="noopener noreferrer"
    class="flex flex-col bg-white rounded-xl border border-slate-200 p-4 transition-all duration-200 cursor-pointer hover:border-brand-300 hover:shadow-md group h-full"
  >
    <!-- Category Tag -->
    <div class="flex items-center justify-between mb-2.5">
      <span
        :class="[
          'inline-flex items-center px-2 py-0.5 rounded text-xs font-medium',
          news.category === '程序员圈'
            ? 'bg-blue-50 text-blue-700'
            : 'bg-emerald-50 text-emerald-700'
        ]"
      >
        {{ news.category }}
      </span>

      <!-- Hot Score (shown in hottest sort mode) -->
      <div
        v-if="showHotScore && news.hot_score > 0"
        class="flex items-center gap-1 text-amber-500"
      >
        <svg class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M12.395 2.553a1 1 0 00-1.45-.385c-.345.23-.614.558-.822.88-.214.33-.403.713-.57 1.116-.334.804-.614 1.768-.84 2.734a31.365 31.365 0 00-.613 3.58 2.64 2.64 0 01-.945-1.067c-.328-.68-.398-1.534-.398-2.654A1 1 0 005.05 6.05 6.981 6.981 0 003 11a7 7 0 1011.95-4.95c-.592-.591-.98-.985-1.348-1.467-.363-.476-.724-1.063-1.207-2.03zM12.12 15.12A3 3 0 017 13s.879.5 2.5.5c0-1 .5-4 1.25-4.5.5 1 .786 1.293 1.371 1.879A2.99 2.99 0 0113 13a2.99 2.99 0 01-.879 2.121z" clip-rule="evenodd" />
        </svg>
        <span class="text-xs font-medium">{{ formatScore(news.hot_score) }}</span>
      </div>
    </div>

    <!-- Title -->
    <h3 class="text-base font-semibold text-slate-900 leading-snug mb-2 line-clamp-2 group-hover:text-brand-600 transition-colors">
      {{ news.title }}
    </h3>

    <!-- Summary - flex-grow to push meta to bottom -->
    <p class="text-sm text-slate-500 leading-relaxed mb-3 line-clamp-2 flex-grow">
      {{ news.summary }}
    </p>

    <!-- Meta Info - always at bottom -->
    <div class="flex items-center justify-between text-xs text-slate-400 mt-auto">
      <!-- Source -->
      <div class="flex items-center gap-1.5 min-w-0">
        <svg class="w-3.5 h-3.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
        </svg>
        <span class="truncate">{{ news.source }}</span>
      </div>

      <!-- Time -->
      <div class="flex items-center gap-1.5 flex-shrink-0">
        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>{{ formatTime(news.published) }}</span>
      </div>
    </div>
  </a>
</template>

<script>
export default {
  name: 'NewsCard',
  props: {
    news: {
      type: Object,
      required: true
    },
    showHotScore: {
      type: Boolean,
      default: false
    }
  },
  setup() {
    // Format relative time
    const formatTime = (dateStr) => {
      if (!dateStr) return ''
      
      const date = new Date(dateStr)
      const now = new Date()
      const diff = now - date
      
      // Less than 1 hour
      if (diff < 3600000) {
        const minutes = Math.floor(diff / 60000)
        return minutes <= 1 ? '刚刚' : `${minutes}分钟前`
      }
      
      // Less than 24 hours
      if (diff < 86400000) {
        const hours = Math.floor(diff / 3600000)
        return `${hours}小时前`
      }
      
      // Less than 7 days
      if (diff < 604800000) {
        const days = Math.floor(diff / 86400000)
        return `${days}天前`
      }
      
      // Show date in YYYY-MM-DD format
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      return `${year}-${month}-${day}`
    }

    // Format hot score
    const formatScore = (score) => {
      if (score >= 1) {
        return score.toFixed(1)
      }
      return score.toFixed(2)
    }

    return {
      formatTime,
      formatScore
    }
  }
}
</script>
