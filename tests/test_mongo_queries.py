from app.db.mongo_queries import (
    avg_duration_by_search_type,
    genre_combinations_raw,
    last5_queries,
    search_type_breakdown,
    searches_per_day,
    success_rate_by_search_type,
    top5_queries,
    top_individual_genres,
    year_range_popularity,
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


class TestYearRangePopularityPipeline:
    def test_is_a_list_of_pipeline_stages(self):
        assert isinstance(year_range_popularity, list)
        assert all(isinstance(stage, dict) for stage in year_range_popularity)

    def test_matches_only_years_and_genre_years_search_types(self):
        match_stage = next(stage["$match"] for stage in year_range_popularity if "$match" in stage)
        assert match_stage["search_type"] == {"$in": ["years", "genre_years"]}

    def test_groups_by_decade_of_start_year(self):
        group_stage = next(stage["$group"] for stage in year_range_popularity if "$group" in stage)
        assert group_stage["_id"] == {
            "$subtract": ["$params.start_year", {"$mod": ["$params.start_year", 10]}]
        }

    def test_sorts_by_count_descending(self):
        sort_stages = [stage["$sort"] for stage in year_range_popularity if "$sort" in stage]
        assert any(sort.get("count") == -1 for sort in sort_stages)

    def test_limits_results(self):
        assert any(stage.get("$limit") for stage in year_range_popularity)


class TestTopIndividualGenresPipeline:
    def test_is_a_list_of_pipeline_stages(self):
        assert isinstance(top_individual_genres, list)
        assert all(isinstance(stage, dict) for stage in top_individual_genres)

    def test_matches_only_genre_and_genre_years_search_types(self):
        match_stage = next(stage["$match"] for stage in top_individual_genres if "$match" in stage)
        assert match_stage["search_type"] == {"$in": ["genre", "genre_years"]}

    def test_unwinds_the_genres_array(self):
        assert any(stage.get("$unwind") == "$params.genres" for stage in top_individual_genres)

    def test_groups_by_individual_genre(self):
        group_stage = next(stage["$group"] for stage in top_individual_genres if "$group" in stage)
        assert group_stage["_id"] == "$params.genres"

    def test_sorts_by_count_descending(self):
        sort_stages = [stage["$sort"] for stage in top_individual_genres if "$sort" in stage]
        assert any(sort.get("count") == -1 for sort in sort_stages)


class TestGenreCombinationsRawPipeline:
    def test_is_a_list_of_pipeline_stages(self):
        assert isinstance(genre_combinations_raw, list)
        assert all(isinstance(stage, dict) for stage in genre_combinations_raw)

    def test_matches_only_genre_and_genre_years_search_types(self):
        match_stage = next(stage["$match"] for stage in genre_combinations_raw if "$match" in stage)
        assert match_stage["search_type"] == {"$in": ["genre", "genre_years"]}

    def test_requires_at_least_two_genres(self):
        match_stage = next(stage["$match"] for stage in genre_combinations_raw if "$match" in stage)
        assert match_stage["params.genres.1"] == {"$exists": True}

    def test_projects_only_the_genres_field(self):
        project_stage = next(stage["$project"] for stage in genre_combinations_raw if "$project" in stage)
        assert project_stage == {"_id": 0, "genres": "$params.genres"}
