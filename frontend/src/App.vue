<template>
  <div class="min-h-screen bg-slate-50 flex flex-col">
    <!-- ========== Header ========== -->
    <header class="bg-white border-b border-slate-200 sticky top-0 z-50">
      <div class="max-w-5xl mx-auto px-4 sm:px-6">
        <div class="flex items-center justify-between h-14">
          <!-- Logo & Title -->
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 rounded-lg bg-brand-600 flex items-center justify-center">
              <!-- Fire icon -->
              <svg class="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M12.395 2.553a1 1 0 00-1.45-.385c-.345.23-.614.558-.822.88-.214.33-.403.713-.57 1.116-.334.804-.614 1.768-.84 2.734a31.365 31.365 0 00-.613 3.58 2.64 2.64 0 01-.945-1.067c-.328-.68-.398-1.534-.398-2.654A1 1 0 005.05 6.05 6.981 6.981 0 003 11a7 7 0 1011.95-4.95c-.592-.591-.98-.985-1.348-1.467-.363-.476-.724-1.063-1.207-2.03zM12.12 15.12A3 3 0 017 13s.879.5 2.5.5c0-1 .5-4 1.25-4.5.5 1 .786 1.293 1.371 1.879A2.99 2.99 0 0113 13a2.99 2.99 0 01-.879 2.121z" clip-rule="evenodd" />
              </svg>
            </div>
            <div class="flex items-center gap-2">
              <h1 class="text-lg font-bold text-slate-900">极客热榜</h1>
              <span class="hidden sm:inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-brand-100 text-brand-700">
                每小时更新
              </span>
            </div>
          </div>

          <!-- Date -->
          <div class="text-sm text-slate-500">
            <span>{{ currentDate }}</span>
          </div>
        </div>
      </div>
    </header>

    <!-- ========== Controls Bar (Sticky) ========== -->
    <div class="bg-white border-b border-slate-200 sticky top-[56px] z-40">
      <div class="max-w-5xl mx-auto px-4 sm:px-6 py-3">
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <!-- Category Tabs -->
          <div class="w-fit flex items-center gap-1 p-1 bg-slate-100 rounded-lg">
            <button
              v-for="cat in categories"
              :key="cat.value"
              @click="switchCategory(cat.value)"
              :class="[
                'px-4 py-1.5 rounded-md text-sm font-medium transition-all duration-200 cursor-pointer',
                currentCategory === cat.value
                  ? 'bg-white text-brand-600 shadow-sm'
                  : 'text-slate-600 hover:text-slate-900'
              ]"
            >
              {{ cat.label }}
            </button>
          </div>

          <!-- Sort Toggle -->
          <div class="flex items-center gap-2">
            <div class="flex items-center bg-slate-100 rounded-lg p-0.5">
              <button
                v-for="sort in sortOptions"
                :key="sort.value"
                @click="switchSort(sort.value)"
                :class="[
                  'px-3 py-1 rounded-md text-sm font-medium transition-all duration-200 cursor-pointer',
                  currentSort === sort.value
                    ? 'bg-white text-slate-900 shadow-sm'
                    : 'text-slate-500 hover:text-slate-700'
                ]"
              >
                {{ sort.label }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ========== Main Content (flex-grow to push footer down) ========== -->
    <main class="flex-grow max-w-5xl mx-auto px-4 sm:px-6 py-6 w-full">
      <!-- Loading State - Skeleton Cards -->
      <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <SkeletonCard v-for="i in 6" :key="i" />
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="text-center py-16">
        <div class="w-14 h-14 mx-auto mb-4 rounded-full bg-red-100 flex items-center justify-center">
          <svg class="w-7 h-7 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
        <p class="text-slate-600 mb-4">{{ error }}</p>
        <button
          @click="fetchNews"
          class="inline-flex items-center gap-2 px-5 py-2 bg-brand-600 text-white rounded-lg font-medium hover:bg-brand-700 transition-colors duration-200 cursor-pointer"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          重新加载
        </button>
      </div>

      <!-- News Grid -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4 items-stretch">
        <NewsCard
          v-for="item in newsItems"
          :key="item.id"
          :news="item"
          :show-hot-score="currentSort === 'hottest'"
        />
      </div>

      <!-- Empty State -->
      <div v-if="!loading && !error && newsItems.length === 0" class="text-center py-16">
        <div class="w-14 h-14 mx-auto mb-4 rounded-full bg-slate-100 flex items-center justify-center">
          <svg class="w-7 h-7 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <p class="text-slate-500">暂无相关资讯</p>
      </div>
    </main>

    <!-- ========== Bottom Bar (Pagination + Copyright, Sticky at bottom) ========== -->
    <div class="bg-white/95">
      <!-- Pagination (only show when multiple pages) -->
      <div v-if="!loading && !error && totalPages > 1" class="max-w-5xl mx-auto px-4 sm:px-6 py-4">
        <nav class="flex items-center justify-center gap-2 sm:gap-4" aria-label="分页导航">
          <!-- Pagination Row -->
          <div class="flex items-center gap-1.5 sm:gap-3">
            <!-- Previous Button -->
            <button
              @click="goToPage(currentPage - 1)"
              :disabled="currentPage === 1"
              class="flex items-center gap-1 px-2 sm:px-4 py-2 text-sm font-medium text-slate-600 rounded-lg border border-slate-200 hover:bg-slate-50 hover:border-slate-300 disabled:opacity-40 disabled:cursor-not-allowed transition-all duration-200 cursor-pointer"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              </svg>
              <span class="hidden sm:inline">上一页</span>
            </button>

            <!-- Page Numbers -->
            <div class="flex items-center gap-1 sm:gap-2">
              <button
                v-for="page in visiblePages"
                :key="page"
                @click="goToPage(page)"
                :class="[
                  'min-w-[36px] sm:min-w-[40px] h-9 sm:h-10 px-2.5 sm:px-3 text-sm font-medium rounded-lg transition-all duration-200 cursor-pointer',
                  page === currentPage
                    ? 'bg-brand-600 text-white shadow-md shadow-brand-600/25'
                    : 'text-slate-600 hover:bg-slate-100 border border-transparent hover:border-slate-200'
                ]"
              >
                {{ page }}
              </button>
            </div>

            <!-- Next Button -->
            <button
              @click="goToPage(currentPage + 1)"
              :disabled="currentPage === totalPages"
              class="flex items-center gap-1 px-2 sm:px-4 py-2 text-sm font-medium text-slate-600 rounded-lg border border-slate-200 hover:bg-slate-50 hover:border-slate-300 disabled:opacity-40 disabled:cursor-not-allowed transition-all duration-200 cursor-pointer"
            >
              <span class="hidden sm:inline">下一页</span>
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>

          <!-- News Count -->
          <div class="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-100 text-slate-500 text-sm">
            <svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
            </svg>
            <span class="font-medium">共 {{ totalNews }} 条</span>
          </div>
          <!-- News Count (mobile - compact) -->
          <div class="sm:hidden flex items-center px-2 py-1 rounded-full bg-slate-100 text-slate-500 text-xs whitespace-nowrap">
            <span class="font-medium">共{{ totalNews }}条</span>
          </div>
        </nav>
      </div>

      <!-- Copyright (always visible) -->
      <div class="border-t border-slate-100 bg-gradient-to-r from-slate-50 via-slate-100/50 to-slate-50 py-3">
        <p class="text-center text-xs text-slate-400 tracking-wide">
          <span class="inline-flex items-center gap-1.5">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            内容版权归原作者所有 · 本站仅提供聚合展示
          </span>
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import NewsCard from './components/NewsCard.vue'
import SkeletonCard from './components/SkeletonCard.vue'

export default {
  name: 'App',
  components: {
    NewsCard,
    SkeletonCard
  },
  setup() {
    // Category options
    const categories = [
      { value: '程序员圈', label: '程序员圈' },
      { value: 'AI圈', label: 'AI圈' }
    ]
    
    // Sort options
    const sortOptions = [
      { value: 'newest', label: '最新' },
      { value: 'hottest', label: '最热' }
    ]
    
    // State
    const currentCategory = ref('程序员圈')
    const currentSort = ref('newest')
    const currentPage = ref(1)
    const totalPages = ref(1)
    const totalNews = ref(0)
    const newsItems = ref([])
    const loading = ref(false)
    const error = ref(null)

    // API base URL
    const API_BASE = import.meta.env.VITE_API_BASE || ''

    // Current date display
    const currentDate = computed(() => {
      const now = new Date()
      const dateStr = now.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
      // const weekday = now.toLocaleDateString('zh-CN', { weekday: 'long' })
      // return `${dateStr} ${weekday}`
      return `${dateStr}`
    })

    // Visible page numbers for pagination
    const visiblePages = computed(() => {
      const pages = []
      const total = totalPages.value
      const current = currentPage.value
      
      let start = Math.max(1, current - 2)
      let end = Math.min(total, current + 2)
      
      // Adjust range to show 5 pages if possible
      if (end - start < 4) {
        if (start === 1) {
          end = Math.min(total, start + 4)
        } else {
          start = Math.max(1, end - 4)
        }
      }
      
      for (let i = start; i <= end; i++) {
        pages.push(i)
      }
      
      return pages
    })

    // Fetch news from API
    const fetchNews = async () => {
      loading.value = true
      error.value = null

      try {
        const params = new URLSearchParams({
          category: currentCategory.value,
          sort: currentSort.value,
          page: currentPage.value
        })

        const response = await fetch(`${API_BASE}/api/news?${params}`)
        if (!response.ok) throw new Error('网络请求失败')
        
        const data = await response.json()
        newsItems.value = data.items
        totalPages.value = data.pages
        totalNews.value = data.total
      } catch (err) {
        console.error('Error fetching news:', err)
        error.value = '加载失败，请稍后重试'
      } finally {
        loading.value = false
      }
    }

    // Switch category and reset to page 1
    const switchCategory = (cat) => {
      if (currentCategory.value !== cat) {
        currentCategory.value = cat
        currentPage.value = 1
      }
    }

    // Switch sort and reset to page 1
    const switchSort = (sort) => {
      if (currentSort.value !== sort) {
        currentSort.value = sort
        currentPage.value = 1
      }
    }

    // Go to specific page
    const goToPage = (page) => {
      if (page >= 1 && page <= totalPages.value && page !== currentPage.value) {
        currentPage.value = page
        window.scrollTo({ top: 0, behavior: 'smooth' })
      }
    }

    // Watch for changes and refetch
    watch([currentCategory, currentSort, currentPage], () => {
      fetchNews()
    })

    // Initial fetch
    onMounted(() => {
      fetchNews()
    })

    return {
      categories,
      sortOptions,
      currentCategory,
      currentSort,
      currentPage,
      totalPages,
      totalNews,
      visiblePages,
      newsItems,
      loading,
      error,
      currentDate,
      fetchNews,
      switchCategory,
      switchSort,
      goToPage
    }
  }
}
</script>
