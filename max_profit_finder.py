
import pandas as pd
import matplotlib.pyplot as plt
import time
import os


def load_prices(filename="prices.csv"):
    df = pd.read_csv(filename)

    required = {"Date", "Close"}
    if not required.issubset(df.columns):
        raise ValueError("CSV must contain Date and Close columns.")

    df["Date"] = pd.to_datetime(df["Date"], errors="raise")
    df["Close"] = pd.to_numeric(df["Close"], errors="raise")

    if df.empty or df["Close"].isna().any():
        raise ValueError("Prices must not be empty or missing.")

    if not all(df["Close"].map(lambda x: x == x and abs(x) != float("inf"))):
        raise ValueError("Prices must be finite numbers.")

    df = df.sort_values("Date").reset_index(drop=True)

    if len(df) < 2:
        raise ValueError("At least two prices are required.")

    return df



def linear_scan(prices):
    comparisons = 0
    min_price = prices[0]
    min_day = 0

    best_profit = 0
    buy_day = sell_day = None

    for day in range(1, len(prices)):
        profit = prices[day] - min_price

        comparisons += 1
        if profit > best_profit:
            best_profit = profit
            buy_day = min_day
            sell_day = day

        comparisons += 1
        if prices[day] < min_price:
            min_price = prices[day]
            min_day = day

    return best_profit, buy_day, sell_day, comparisons


def divide_conquer(prices):
    
    changes = [
        prices[i + 1] - prices[i]
        for i in range(len(prices) - 1)
    ]
    comparisons = [0]

    def max_subarray(left, right):
        if left == right:
            return changes[left], left, right

        mid = (left + right) // 2

        left_sum, left_start, left_end = max_subarray(left, mid)
        right_sum, right_start, right_end = max_subarray(
            mid + 1, right
        )

        
        total = 0
        best_left_sum = float("-inf")
        cross_start = mid

        for i in range(mid, left - 1, -1):
            total += changes[i]
            comparisons[0] += 1
            if total > best_left_sum:
                best_left_sum = total
                cross_start = i

        total = 0
        best_right_sum = float("-inf")
        cross_end = mid + 1

        for i in range(mid + 1, right + 1):
            total += changes[i]
            comparisons[0] += 1
            if total > best_right_sum:
                best_right_sum = total
                cross_end = i

        cross_sum = best_left_sum + best_right_sum

        
        comparisons[0] += 1
        if left_sum >= right_sum and left_sum >= cross_sum:
            return left_sum, left_start, left_end

        comparisons[0] += 1
        if right_sum >= left_sum and right_sum >= cross_sum:
            return right_sum, right_start, right_end

        return cross_sum, cross_start, cross_end

    best_sum, start, end = max_subarray(0, len(changes) - 1)

   
    if best_sum <= 0:
        return 0, None, None, comparisons[0]

    
    return best_sum, start, end + 1, comparisons[0]




def merge_sort_animated(values, delay=0.15):
    arr = values.copy()
    comparisons = [0]

    plt.ion()
    fig, ax = plt.subplots()
    fig.canvas.manager.set_window_title("Merge Sort")

    def draw(highlight=()):
        ax.clear()
        colors = [
            "tomato" if i in highlight else "steelblue"
            for i in range(len(arr))
        ]
        ax.bar(range(len(arr)), arr, color=colors)
        ax.set_title(
            f"Merge Sort | Comparisons: {comparisons[0]}"
        )
        ax.set_xlabel("Index")
        ax.set_ylabel("Price")
        fig.canvas.draw_idle()
        plt.pause(delay)

    def sort(left, right):
        if right - left <= 1:
            return

        mid = (left + right) // 2
        sort(left, mid)
        sort(mid, right)

        L = arr[left:mid]
        R = arr[mid:right]
        i = j = 0
        k = left

        while i < len(L) and j < len(R):
            comparisons[0] += 1
            draw((k,))

            if L[i] <= R[j]:
                arr[k] = L[i]
                i += 1
            else:
                arr[k] = R[j]
                j += 1

            k += 1
            draw((k - 1,))

        while i < len(L):
            arr[k] = L[i]
            i += 1
            k += 1
            draw((k - 1,))

        while j < len(R):
            arr[k] = R[j]
            j += 1
            k += 1
            draw((k - 1,))

    draw()
    sort(0, len(arr))
    draw()
    ax.set_title(f"Merge Sort Complete | Comparisons: {comparisons[0]}")
    plt.ioff()
    plt.show()

    return arr, comparisons[0]


def quick_sort_animated(values, delay=0.15):
    arr = values.copy()
    comparisons = [0]

    plt.ion()
    fig, ax = plt.subplots()
    fig.canvas.manager.set_window_title("Quick Sort")

    def draw(highlight=()):
        ax.clear()
        colors = [
            "tomato" if i in highlight else "seagreen"
            for i in range(len(arr))
        ]
        ax.bar(range(len(arr)), arr, color=colors)
        ax.set_title(
            f"Quick Sort | Comparisons: {comparisons[0]}"
        )
        ax.set_xlabel("Index")
        ax.set_ylabel("Price")
        fig.canvas.draw_idle()
        plt.pause(delay)

    def partition(low, high):
        pivot = arr[high]
        i = low - 1

        for j in range(low, high):
            comparisons[0] += 1
            draw((j, high))

            if arr[j] <= pivot:
                i += 1
                arr[i], arr[j] = arr[j], arr[i]
                draw((i, j, high))

        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        draw((i + 1,))
        return i + 1

    def sort(low, high):
        if low < high:
            pivot_index = partition(low, high)
            sort(low, pivot_index - 1)
            sort(pivot_index + 1, high)

    draw()
    sort(0, len(arr) - 1)
    draw()
    ax.set_title(f"Quick Sort Complete | Comparisons: {comparisons[0]}")
    plt.ioff()
    plt.show()

    return arr, comparisons[0]



def show_result(df, result, algorithm):
    profit, buy, sell, comparisons = result

    print(f"\n--- {algorithm} ---")
    print(f"Maximum profit: {profit:.2f}")
    print(f"Comparisons: {comparisons}")

    if buy is None:
        print("No profitable transaction.")
    else:
        print(f"Buy date:  {df.loc[buy, 'Date'].date()}")
        print(f"Buy price: {df.loc[buy, 'Close']:.2f}")
        print(f"Sell date: {df.loc[sell, 'Date'].date()}")
        print(f"Sell price: {df.loc[sell, 'Close']:.2f}")


def plot_prices(df, result):
    profit, buy, sell, _ = result

    plt.figure(figsize=(10, 5))
    plt.plot(df["Date"], df["Close"], marker="o", label="Close price")

    if buy is not None:
        plt.scatter(
            df.loc[buy, "Date"], df.loc[buy, "Close"],
            color="green", s=120, label="Buy"
        )
        plt.scatter(
            df.loc[sell, "Date"], df.loc[sell, "Close"],
            color="red", s=120, label="Sell"
        )
        plt.plot(
            df.loc[[buy, sell], "Date"],
            df.loc[[buy, sell], "Close"],
            linestyle="--", color="orange"
        )

    plt.title(f"Max Profit Finder | Profit: {profit:.2f}")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend()
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.show()


def main():
    filename = input(
        "CSV filename [prices.csv]: "
    ).strip() or "prices.csv"

    try:
        df = load_prices(filename)
    except (OSError, ValueError, KeyError) as error:
        print(f"Could not load data: {error}")
        return

    prices = df["Close"].tolist()

    print("\nPrice data:")
    print(df.to_string(index=False))

    linear = linear_scan(prices)
    divide = divide_conquer(prices)

    show_result(df, linear, "Linear Scan")
    show_result(df, divide, "Divide and Conquer")

    print("\n--- Result Verification ---")
    if linear[0] == divide[0]:
        print("Both algorithms found the same maximum profit.")
    else:
        print("Warning: The algorithms returned different profits.")

    print("\n--- Sorting Algorithms ---")
    print("1. Run Merge Sort animation")
    print("2. Run Quick Sort animation")
    print("3. Run both animations")
    print("4. Skip sorting animations")

    choice = input("Choose (1-4): ").strip()

    if choice in ("1", "3"):
        sorted_merge, merge_count = merge_sort_animated(prices)
        print("\nMerge Sort comparisons:", merge_count)
        print("Sorted prices:", sorted_merge)

    if choice in ("2", "3"):
        sorted_quick, quick_count = quick_sort_animated(prices)
        print("\nQuick Sort comparisons:", quick_count)
        print("Sorted prices:", sorted_quick)

    plot_prices(df, linear)


if __name__ == "__main__":
    main()
