from app.db.mongo_queries import last5_queries, top5_queries


class TestTop5QueriesPipeline:
    def test_is_a_list_of_pipeline_stages(self):
        assert isinstance(top5_queries, list)
        assert all(isinstance(stage, dict) for stage in top5_queries)

    def test_groups_by_query_key(self):
        assert any("$group" in stage and stage["$group"].get("_id") == "$query_key" for stage in top5_queries)

    def test_limits_to_five(self):
        assert any(stage.get("$limit") == 5 for stage in top5_queries)

    def test_sorts_by_count_descending(self):
        sort_stages = [stage["$sort"] for stage in top5_queries if "$sort" in stage]
        assert any(sort.get("count") == -1 for sort in sort_stages)


class TestLast5QueriesPipeline:
    def test_is_a_list_of_pipeline_stages(self):
        assert isinstance(last5_queries, list)
        assert all(isinstance(stage, dict) for stage in last5_queries)

    def test_limits_to_five(self):
        assert any(stage.get("$limit") == 5 for stage in last5_queries)

    def test_deduplicates_by_query_key(self):
        assert any("$group" in stage and stage["$group"].get("_id") == "$query_key" for stage in last5_queries)

    def test_sorts_by_timestamp_descending(self):
        sort_stages = [stage["$sort"] for stage in last5_queries if "$sort" in stage]
        assert any(sort.get("timestamp") == -1 for sort in sort_stages)
