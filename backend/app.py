@app.route('/api/categories', methods=['GET'])
@cache.cached(timeout=3600)
def get_categories():
    """Get all available categories in predefined order."""
    # Directly return predefined categories to avoid expensive database queries
    categories = ['AI', '前端', '后端', '云原生', '区块链', '其他']
    return jsonify(categories)