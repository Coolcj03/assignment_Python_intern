# algorithms.py

class Sorting:
    """A collection of sorting algorithms."""

    def quicksort(self, data: list, sort_by: str, ascending: bool = True):
        """
        Sorts a list of dictionaries using the Quicksort algorithm.
        Time complexity: O(n log n) on average, O(n^2) in the worst case.
        
        Args:
            data (list): A list of dictionaries to sort.
            sort_by (str): The key in the dictionary to sort by.
            ascending (bool): True for ascending, False for descending.
        
        Returns:
            list: The sorted list.
        """
        if len(data) < 2:
            return data
        
        # Make a copy to not modify the original list
        arr = list(data)
        
        # The stack for the iterative version of quicksort
        stack = [(0, len(arr) - 1)]

        while stack:
            low, high = stack.pop()
            
            if low >= high:
                continue

            # Partitioning
            pivot = arr[(low + high) // 2][sort_by]
            i, j = low, high
            
            while i <= j:
                while (arr[i][sort_by] < pivot) if ascending else (arr[i][sort_by] > pivot):
                    i += 1
                while (arr[j][sort_by] > pivot) if ascending else (arr[j][sort_by] < pivot):
                    j -= 1
                
                if i <= j:
                    arr[i], arr[j] = arr[j], arr[i]
                    i += 1
                    j -= 1
            
            # Push subarrays onto the stack
            if low < j:
                stack.append((low, j))
            if i < high:
                stack.append((i, high))
                
        return arr

class Searching:
    """A collection of searching algorithms."""

    def keyword_search(self, data: list, query: str, search_fields: list):
        """
        Performs a keyword search across specified fields in a list of dictionaries.
        This is a linear search, O(n*m*k) where n is # of items, m is # of fields, 
        and k is # of query terms.
        
        Args:
            data (list): The list of dictionaries to search.
            query (str): The search query string.
            search_fields (list): A list of keys to search within each dictionary.
            
        Returns:
            list: A list of matching dictionaries with a 'relevance_score'.
        """
        if not query:
            return data
            
        query_terms = query.lower().split()
        results = []
        
        for item in data:
            score = 0
            for field in search_fields:
                if field in item and item[field]:
                    field_text = str(item[field]).lower()
                    for term in query_terms:
                        if term in field_text:
                            score += field_text.count(term)
            
            if score > 0:
                item_copy = item.copy()
                item_copy['relevance_score'] = score
                results.append(item_copy)
                
        # Sort results by relevance score
        return sorted(results, key=lambda x: x['relevance_score'], reverse=True)

class Aggregation:
    """A collection of aggregation functions."""

    def calculate_median(self, numbers: list):
        """Calculates the median of a list of numbers."""
        if not numbers:
            return 0
        sorted_nums = sorted(numbers)
        n = len(sorted_nums)
        mid = n // 2
        if n % 2 == 0:
            return (sorted_nums[mid - 1] + sorted_nums[mid]) / 2
        else:
            return sorted_nums[mid]

    def calculate_mode(self, data: list):
        """Calculates the mode of a list."""
        if not data:
            return None
        return max(set(data), key=data.count)

    def time_series_aggregation(self, data: list, date_field: str, value_field: str, period: str = 'M'):
        """
        Aggregates data into a time-series.
        
        Args:
            data (list): List of dictionaries with date and value fields.
            date_field (str): The name of the date field.
            value_field (str): The name of the numeric field to aggregate.
            period (str): 'M' for monthly, 'W' for weekly, 'D' for daily.
        
        Returns:
            dict: A dictionary of period -> aggregated value.
        """
        if not data:
            return {}
        
        # Using pandas here because it's the right tool for time-series
        import pandas as pd
        
        df = pd.DataFrame(data)
        if date_field not in df.columns or value_field not in df.columns:
            return {}
            
        df[date_field] = pd.to_datetime(df[date_field], errors='coerce')
        df = df.dropna(subset=[date_field])
        
        df = df.set_index(date_field)
        aggregated = df[value_field].resample(period).sum()
        
        return {str(k.to_period()): v for k, v in aggregated.to_dict().items()}

    def group_and_aggregate(self, data: list, group_by_key: str, aggregations: dict):
        """
        Groups a list of dictionaries and performs specified aggregations.

        Args:
            data (list): The list of dictionaries to process.
            group_by_key (str): The key to group the data by.
            aggregations (dict): Defines aggregations. 
                                 Example: {'amount': ['sum', 'avg'], 'id': ['count']}
        
        Returns:
            dict: A dictionary where keys are groups and values are aggregated results.
        """
        grouped_data = {}

        # First pass: collect data for each group
        for item in data:
            key = item.get(group_by_key)
            if key is None:
                continue

            if key not in grouped_data:
                grouped_data[key] = { agg_field: [] for agg_field in aggregations }
            
            for agg_field in aggregations:
                if agg_field in item:
                    grouped_data[key][agg_field].append(item[agg_field])
        
        # Second pass: compute aggregations
        results = {}
        for key, values in grouped_data.items():
            result_item = {}
            for agg_field, agg_funcs in aggregations.items():
                field_values = [v for v in values[agg_field] if isinstance(v, (int, float))]
                
                for func in agg_funcs:
                    agg_key = f"{agg_field}_{func}"
                    if func == 'sum':
                        result_item[agg_key] = sum(field_values)
                    elif func == 'avg':
                        result_item[agg_key] = sum(field_values) / len(field_values) if field_values else 0
                    elif func == 'count':
                        result_item[agg_key] = len(values[agg_field])

            results[key] = result_item
            
        return results 