from app.db.mongo_queries import (
    avg_duration_by_search_type,
    last5_queries,
    search_type_breakdown,
    searches_per_day,
    success_rate_by_search_type,
    top5_queries,
    zero_result_queries,
)


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


class TestZeroResultQueriesPipeline:
    def test_is_a_list_of_pipeline_stages(self):
        assert isinstance(zero_result_queries, list)
        assert all(isinstance(stage, dict) for stage in zero_result_queries)

    def test_matches_only_zero_result_documents(self):
        assert any(
            "$match" in stage and stage["$match"].get("results_count") == 0
            for stage in zero_result_queries
        )

    def test_groups_by_query_key(self):
        assert any(
            "$group" in stage and stage["$group"].get("_id") == "$query_key"
            for stage in zero_result_queries
        )

    def test_limits_results(self):
        assert any(stage.get("$limit") for stage in zero_result_queries)

    def test_sorts_by_count_descending(self):
        sort_stages = [stage["$sort"] for stage in zero_result_queries if "$sort" in stage]
        assert any(sort.get("count") == -1 for sort in sort_stages)


class TestSearchTypeBreakdownPipeline:
    def test_is_a_list_of_pipeline_stages(self):
        assert isinstance(search_type_breakdown, list)
        assert all(isinstance(stage, dict) for stage in search_type_breakdown)

    def test_groups_by_search_type(self):
        assert any(
            "$group" in stage and stage["$group"].get("_id") == "$search_type"
            for stage in search_type_breakdown
        )

    def test_sorts_by_count_descending(self):
        sort_stages = [stage["$sort"] for stage in search_type_breakdown if "$sort" in stage]
        assert any(sort.get("count") == -1 for sort in sort_stages)


class TestAvgDurationBySearchTypePipeline:
    def test_is_a_list_of_pipeline_stages(self):
        assert isinstance(avg_duration_by_search_type, list)
        assert all(isinstance(stage, dict) for stage in avg_duration_by_search_type)

    def test_groups_by_search_type_with_average(self):
        group_stage = next(stage["$group"] for stage in avg_duration_by_search_type if "$group" in stage)
        assert group_stage.get("_id") == "$search_type"
        assert group_stage.get("avg_duration_ms") == {"$avg": "$duration_ms"}

    def test_sorts_by_avg_duration_descending(self):
        sort_stages = [stage["$sort"] for stage in avg_duration_by_search_type if "$sort" in stage]
        assert any(sort.get("avg_duration_ms") == -1 for sort in sort_stages)


class TestSearchesPerDayPipeline:
    def test_is_a_list_of_pipeline_stages(self):
        assert isinstance(searches_per_day, list)
        assert all(isinstance(stage, dict) for stage in searches_per_day)

    def test_groups_by_formatted_date(self):
        group_stage = next(stage["$group"] for stage in searches_per_day if "$group" in stage)
        assert group_stage["_id"] == {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}}

    def test_sorts_by_date_descending(self):
        sort_stages = [stage["$sort"] for stage in searches_per_day if "$sort" in stage]
        assert any(sort.get("_id") == -1 for sort in sort_stages)

    def test_limits_to_fourteen_days(self):
        assert any(stage.get("$limit") == 14 for stage in searches_per_day)


class TestSuccessRateBySearchTypePipeline:
    def test_is_a_list_of_pipeline_stages(self):
        assert isinstance(success_rate_by_search_type, list)
        assert all(isinstance(stage, dict) for stage in success_rate_by_search_type)

    def test_groups_by_search_type_counting_success(self):
        group_stage = next(stage["$group"] for stage in success_rate_by_search_type if "$group" in stage)
        assert group_stage.get("_id") == "$search_type"
        assert "successful" in group_stage

    def test_computes_percentage_via_project_stage(self):
        project_stage = next(
            stage["$project"] for stage in success_rate_by_search_type if "$project" in stage
        )
        assert "success_rate_pct" in project_stage
