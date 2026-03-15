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
        <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-3">
          <!-- Category Tabs -->
          <div class="relative w-fit max-w-full">
            <!-- Left fade indicator -->
            <div class="absolute left-0 top-0 bottom-0 w-4 bg-gradient-to-r from-white to-transparent z-10 pointer-events-none opacity-0 transition-opacity duration-200" ref="leftFade"></div>
            <!-- Right fade indicator -->
            <div class="absolute right-0 top-0 bottom-0 w-4 bg-gradient-to-l from-white to-transparent z-10 pointer-events-none" ref="rightFade"></div>
            <!-- Scrollable tabs with background -->
            <div 
              class="overflow-x-auto scrollbar-hide p-1 bg-slate-100 rounded-lg" 
              ref="categoryScroll"
              @scroll="handleCategoryScroll"
            >
              <div class="flex items-center gap-1 whitespace-nowrap">
                <button
                  v-for="cat in categories"
                  :key="cat.value"
                  @click="switchCategory(cat.value, $event)"
                  :class="[
                    'px-3 sm:px-4 py-1.5 rounded-md text-sm font-medium transition-all duration-200 cursor-pointer flex-shrink-0',
                    currentCategory === cat.value
                      ? 'bg-white text-brand-600 shadow-sm'
                      : 'text-slate-600 hover:text-slate-900'
                  ]"
                >
                  {{ cat.label }}
                </button>
              </div>
            </div>
          </div>

          <!-- Sort Toggle -->
          <div class="flex items-center gap-2 flex-shrink-0">
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
      <!-- Pagination (always show when has data) -->
      <div v-if="!loading && !error && totalNews > 0" class="max-w-5xl mx-auto px-3 sm:px-6 py-3 sm:py-4">
        <nav class="flex flex-col sm:flex-row items-center justify-center gap-2 sm:gap-4" aria-label="分页导航">
          <!-- Pagination Controls -->
          <div class="flex items-center gap-1 sm:gap-1.5">
            <!-- Previous Button -->
            <button
              @click="goToPage(currentPage - 1)"
              :disabled="currentPage === 1"
              class="flex items-center justify-center w-8 h-8 sm:w-9 sm:h-9 text-sm font-medium text-slate-600 rounded-lg border border-slate-200 hover:bg-slate-50 hover:border-slate-300 disabled:opacity-40 disabled:cursor-not-allowed transition-all duration-200 cursor-pointer"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              </svg>
            </button>

            <!-- First Page -->
            <button
              v-if="showFirstPage"
              @click="goToPage(1)"
              :class="[
                'flex items-center justify-center w-8 h-8 sm:w-9 sm:h-9 text-sm font-medium rounded-lg transition-all duration-200 cursor-pointer',
                1 === currentPage
                  ? 'bg-brand-600 text-white shadow-sm'
                  : 'text-slate-600 hover:bg-slate-100'
              ]"
            >
              1
            </button>

            <!-- Left Ellipsis -->
            <button
              v-if="showLeftEllipsis"
              @click="goToPage(Math.max(1, currentPage - 5))"
              class="flex items-center justify-center w-8 h-8 sm:w-9 sm:h-9 text-sm font-medium text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-100 transition-all duration-200 cursor-pointer"
              title="向前5页"
            >
              <span class="hidden sm:inline">•••</span>
              <span class="sm:hidden">•</span>
            </button>

            <!-- Page Numbers -->
            <button
              v-for="page in visiblePages"
              :key="page"
              @click="goToPage(page)"
              :class="[
                'flex items-center justify-center w-8 h-8 sm:w-9 sm:h-9 text-sm font-medium rounded-lg transition-all duration-200 cursor-pointer',
                page === currentPage
                  ? 'bg-brand-600 text-white shadow-sm'
                  : 'text-slate-600 hover:bg-slate-100'
              ]"
            >
              {{ page }}
            </button>

            <!-- Right Ellipsis -->
            <button
              v-if="showRightEllipsis"
              @click="goToPage(Math.min(totalPages, currentPage + 5))"
              class="flex items-center justify-center w-8 h-8 sm:w-9 sm:h-9 text-sm font-medium text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-100 transition-all duration-200 cursor-pointer"
              title="向后5页"
            >
              <span class="hidden sm:inline">•••</span>
              <span class="sm:hidden">•</span>
            </button>

            <!-- Last Page -->
            <button
              v-if="showLastPage"
              @click="goToPage(totalPages)"
              :class="[
                'flex items-center justify-center w-8 h-8 sm:w-9 sm:h-9 text-sm font-medium rounded-lg transition-all duration-200 cursor-pointer',
                totalPages === currentPage
                  ? 'bg-brand-600 text-white shadow-sm'
                  : 'text-slate-600 hover:bg-slate-100'
              ]"
            >
              {{ totalPages }}
            </button>

            <!-- Next Button -->
            <button
              @click="goToPage(currentPage + 1)"
              :disabled="currentPage === totalPages"
              class="flex items-center justify-center w-8 h-8 sm:w-9 sm:h-9 text-sm font-medium text-slate-600 rounded-lg border border-slate-200 hover:bg-slate-50 hover:border-slate-300 disabled:opacity-40 disabled:cursor-not-allowed transition-all duration-200 cursor-pointer"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>

          <!-- Page Size Selector, Jump Input & Total Count -->
          <div class="flex items-center gap-2 sm:gap-3">
            <!-- Page Size Selector -->
            <div class="flex items-center gap-1 text-xs sm:text-sm text-slate-600">
              <span>每页</span>
              <select
                :value="pageSize"
                @change="handlePageSizeChange($event)"
                class="h-7 sm:h-8 px-1.5 sm:px-2 text-xs sm:text-sm font-medium text-slate-700 bg-white border border-slate-200 rounded focus:outline-none focus:ring-1 focus:ring-brand-500 focus:border-brand-500 cursor-pointer"
              >
                <option :value="10">10</option>
                <option :value="20">20</option>
                <option :value="50">50</option>
                <option :value="100">100</option>
              </select>
              <span>条</span>
            </div>

            <!-- Jump to Page Input -->
            <div class="hidden md:flex items-center gap-1 text-xs sm:text-sm text-slate-600">
              <span>跳至</span>
              <input
                v-model.number="jumpPageInput"
                @keyup.enter="handleJumpPage"
                type="number"
                min="1"
                :max="totalPages"
                class="w-10 sm:w-12 h-7 sm:h-8 px-1 text-xs sm:text-sm font-medium text-center text-slate-700 bg-white border border-slate-200 rounded focus:outline-none focus:ring-1 focus:ring-brand-500 focus:border-brand-500"
                placeholder=""
              />
              <span>页</span>
            </div>

            <!-- Total Count Badge -->
            <div class="flex items-center gap-1.5 px-2 sm:px-2.5 py-1 rounded-full bg-slate-100 text-slate-500 text-xs sm:text-sm">
              <svg class="w-3 h-3 sm:w-3.5 sm:h-3.5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
              </svg>
              <span class="font-medium">共 {{ totalNews }} 条</span>
            </div>
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
import { inject } from '@vercel/analytics'
import NewsCard from './components/NewsCard.vue'
import SkeletonCard from './components/SkeletonCard.vue'

export default {
  name: 'App',
  components: {
    NewsCard,
    SkeletonCard
  },
  setup() {
    // Category options (will be fetched from API)
    const categories = ref([])
    
    // Sort options
    const sortOptions = [
      { value: 'newest', label: '最新' },
      { value: 'hottest', label: '最热' }
    ]
    
    // State
    const currentCategory = ref('')
    const currentSort = ref('newest')
    const currentPage = ref(1)
    const pageSize = ref(20)
    const totalPages = ref(1)
    const totalNews = ref(0)
    const newsItems = ref([])
    const loading = ref(true)
    const error = ref(null)
    const jumpPageInput = ref('')
    
    // Refs for category scroll
    const categoryScroll = ref(null)
    const leftFade = ref(null)
    const rightFade = ref(null)

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

    // Show first page button
    const showFirstPage = computed(() => {
      return totalPages.value > 1 && visiblePages.value[0] > 1
    })

    // Show last page button
    const showLastPage = computed(() => {
      return totalPages.value > 1 && visiblePages.value[visiblePages.value.length - 1] < totalPages.value
    })

    // Show left ellipsis
    const showLeftEllipsis = computed(() => {
      return visiblePages.value[0] > 2
    })

    // Show right ellipsis
    const showRightEllipsis = computed(() => {
      return visiblePages.value[visiblePages.value.length - 1] < totalPages.value - 1
    })

    // Visible page numbers for pagination (Ant Design style)
    // Shows max 3 pages in the middle: 1 ... 3 4 5 ... 10
    const visiblePages = computed(() => {
      const pages = []
      const total = totalPages.value
      const current = currentPage.value
      const maxVisible = 3 // Show at most 3 page numbers in the middle
      
      // If total pages is small (<= 5), show all
      if (total <= 5) {
        for (let i = 1; i <= total; i++) {
          pages.push(i)
        }
        return pages
      }
      
      // For larger page counts, show: 1 ... [current-1, current, current+1] ... total
      // Calculate middle range (excluding first and last page)
      let start = Math.max(2, current - 1)
      let end = Math.min(total - 1, current + 1)
      
      // Adjust to show maxVisible pages
      if (end - start + 1 < maxVisible) {
        if (start === 2) {
          end = Math.min(total - 1, start + maxVisible - 1)
        } else {
          start = Math.max(2, end - maxVisible + 1)
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
          page: currentPage.value,
          per_page: pageSize.value
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
    const switchCategory = (cat, event) => {
      if (currentCategory.value !== cat) {
        currentCategory.value = cat
        currentPage.value = 1
      }
      
      // Scroll clicked button into view
      if (event && event.target) {
        const button = event.target
        const scrollContainer = categoryScroll.value
        if (scrollContainer) {
          const buttonRect = button.getBoundingClientRect()
          const containerRect = scrollContainer.getBoundingClientRect()
          
          // Check if button is outside the visible area
          if (buttonRect.left < containerRect.left || buttonRect.right > containerRect.right) {
            button.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' })
          }
        }
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

    // Handle page size change - reset to page 1 and fetch
    const handlePageSizeChange = (event) => {
      // Update pageSize from the select event
      pageSize.value = parseInt(event.target.value)
      // Force page reset and fetch
      currentPage.value = 1
      // Use nextTick to ensure the DOM updates before fetching
      setTimeout(() => {
        fetchNews()
      }, 0)
    }

    // Handle jump to page
    const handleJumpPage = () => {
      const page = parseInt(jumpPageInput.value)
      if (page && page >= 1 && page <= totalPages.value) {
        goToPage(page)
        jumpPageInput.value = ''
      }
    }

    // Handle category scroll to show/hide fade indicators
    const handleCategoryScroll = () => {
      if (!categoryScroll.value || !leftFade.value || !rightFade.value) return
      
      const { scrollLeft, scrollWidth, clientWidth } = categoryScroll.value
      const isScrollable = scrollWidth > clientWidth
      
      // Show left fade if scrolled right
      leftFade.value.style.opacity = scrollLeft > 0 ? '1' : '0'
      
      // Show right fade if not scrolled to end
      const isAtEnd = scrollLeft >= scrollWidth - clientWidth - 1
      rightFade.value.style.opacity = isScrollable && !isAtEnd ? '1' : '0'
    }

    // Watch for changes and refetch (excluding pageSize which is handled manually)
    watch([currentCategory, currentSort, currentPage], () => {
      fetchNews()
    })

    // Fetch categories from API
    const fetchCategories = async () => {
      try {
        const response = await fetch(`${API_BASE}/api/categories`)
        if (!response.ok) throw new Error('Failed to fetch categories')
        
        const data = await response.json()
        // Transform to { value, label } format
        categories.value = data.map(cat => ({ value: cat, label: cat }))
        
        // Set default category if current one is not in the list
        if (categories.value.length > 0 && !categories.value.find(c => c.value === currentCategory.value)) {
          currentCategory.value = categories.value[0].value
        }
        
        // Update scroll fade indicators after categories load
        setTimeout(handleCategoryScroll, 100)
      } catch (err) {
        console.error('Error fetching categories:', err)
        // Fallback categories - empty array, will show loading state
        categories.value = []
      }
    }

    // Initial fetch
    onMounted(() => {
      inject()
      // Fetch categories first, then the watcher will trigger fetchNews
      // after the first category is set (avoiding fetching all data)
      fetchCategories()
      // Update fade indicators on window resize
      window.addEventListener('resize', handleCategoryScroll)
    })

    return {
      categories,
      sortOptions,
      currentCategory,
      currentSort,
      currentPage,
      pageSize,
      totalPages,
      totalNews,
      visiblePages,
      showFirstPage,
      showLastPage,
      showLeftEllipsis,
      showRightEllipsis,
      newsItems,
      loading,
      error,
      currentDate,
      jumpPageInput,
      categoryScroll,
      leftFade,
      rightFade,
      fetchNews,
      fetchCategories,
      handleCategoryScroll,
      handlePageSizeChange,
      handleJumpPage,
      switchCategory,
      switchSort,
      goToPage
    }
  }
}
</script>

<style>
/* Hide scrollbar for Chrome, Safari and Opera */
.scrollbar-hide::-webkit-scrollbar {
  display: none;
}

/* Hide scrollbar for IE, Edge and Firefox */
.scrollbar-hide {
  -ms-overflow-style: none;  /* IE and Edge */
  scrollbar-width: none;  /* Firefox */
}
</style>
