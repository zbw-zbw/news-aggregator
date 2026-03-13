<template>
  <div class="flex flex-col bg-white rounded-xl border border-slate-200 p-4 h-full">
    <!-- Category Tag Skeleton -->
    <div class="flex items-center justify-between mb-2.5">
      <div class="h-5 w-16 rounded skeleton-shimmer"></div>
      <div class="h-4 w-8 rounded skeleton-shimmer"></div>
    </div>

    <!-- Title Skeleton -->
    <div class="space-y-2 mb-2">
      <div class="h-5 w-full rounded skeleton-shimmer"></div>
      <div class="h-5 w-3/4 rounded skeleton-shimmer"></div>
    </div>

    <!-- Summary Skeleton - flex-grow to match NewsCard -->
    <div class="space-y-1.5 mb-3 flex-grow">
      <div class="h-4 w-full rounded skeleton-shimmer"></div>
      <div class="h-4 w-5/6 rounded skeleton-shimmer"></div>
    </div>

    <!-- Meta Info Skeleton - mt-auto to push to bottom -->
    <div class="flex items-center justify-between mt-auto">
      <div class="h-3.5 w-20 rounded skeleton-shimmer"></div>
      <div class="h-3.5 w-14 rounded skeleton-shimmer"></div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SkeletonCard'
}
</script>
