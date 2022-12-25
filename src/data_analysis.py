import re
from time import perf_counter

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import wilcoxon, mannwhitneyu, ranksums

from model.market import exponential_model, logistics_model
from model.navigation import Location


palette = {
        "naive": "tab:blue",
        "careful" : "tab:blue",
        "smart": "tab:blue",
        "sceptical": "tab:blue",
        "greedy": "limegreen",
        "saboteur": "firebrick",
        "smartboteur": "firebrick",
        "scaboteur": "firebrick",
    }

name_conversion = {
    "honest" : "naive",
    "smart" : "sceptical",
    "smartboteur" : "scaboteur"
}

def main():
    dec_const = pd.read_csv("../data/old_data/results_decaying_constant.txt", header=None).values.flatten()
    w_dec_const = pd.read_csv("../data/old_data/results_weighteddecaying_constant.txt", header=None).values.flatten()
    better = pd.read_csv("../data/old_data/results_betterage.txt", header=None).values.flatten()
    w_better = pd.read_csv("../data/old_data/results_weightedbetterage.txt", header=None).values.flatten()
    dec_lin = pd.read_csv("../data/old_data/results_decaying_linearnoise.txt", header=None).values.flatten()
    w_dec_lin = pd.read_csv("../data/old_data/results_weighteddecaying_linearnoise.txt", header=None).values.flatten()
    dec_exp = pd.read_csv("../data/old_data/results_decaying_expnoise.txt", header=None).values.flatten()
    w_dec_exp = pd.read_csv("../data/old_data/results_weighteddecaying_expnoise.txt", header=None).values.flatten()
    dec_exp_const = pd.read_csv("../data/old_data/results_decaying_expconst.txt", header=None).values.flatten()
    # print(dec_const.mean(axis=1).mean())
    # print(better.mean(axis=1).mean())
    # print(dec_lin.mean(axis=1).mean())
    fig, axs = plt.subplots(1, 6, sharey=True)
    fig.set_size_inches(12, 6)
    pd.DataFrame(dec_const).boxplot(ax=axs[0]).set_title("Decaying Constant")
    pd.DataFrame(w_dec_const).boxplot(ax=axs[1]).set_title("W-Decaying Constant")
    # pd.DataFrame(better).boxplot(ax=axs[2]).set_title("Better Age")
    # pd.DataFrame(w_better).boxplot(ax=axs[3]).set_title("W-Better Age")
    pd.DataFrame(dec_lin).boxplot(ax=axs[2]).set_title("Decaying Linear")
    pd.DataFrame(w_dec_lin).boxplot(ax=axs[3]).set_title("W-Decaying Linear")
    pd.DataFrame(dec_exp).boxplot(ax=axs[4]).set_title("Decaying Exp")
    pd.DataFrame(w_dec_exp).boxplot(ax=axs[5]).set_title("W-Decaying Exp")
    # pd.DataFrame(dec_exp_const).boxplot(ax=axs[5]).set_title("Dec Exp Const")
    plt.show()


def main2():
    df = pd.read_csv("../data/behaviors/rewards/25honest.txt", header=None)
    plt.plot(df.apply(np.mean, axis=0))
    plt.show()


def compare_strats():
    strats = ["age", "w-age", "lin", "w-lin", "exp", "w-exp"]
    strats_translated = {
        "age" : "Constant",
        "w-age" : "W-Constant",
        "lin" : "Linear",
        "w-lin" : "W-Linear",
        "exp" : "Exponential",
        "w-exp" : "W-Exponential"
    }
    mu_folders = ["low_0", "med_05", "high_10"]
    sd_folders = ["low_01", "high_10"]
    popsize_folders = {"low_10", "high_50"}
    d = {"mu": mu_folders, "sd": sd_folders, "popsize": popsize_folders}
    for f1 in d:
        fig, axs = plt.subplots(1, len(d[f1]), sharey=True)
        fig.suptitle("Comparing different ways to decrease quality and to combine location information")
        fig.set_size_inches(8*len(d[f1]), 6)
        for i, f2 in enumerate(d[f1]):
            print(axs[i])
            items_tot = []
            strategies_tot = []
            for s in strats:
                items = (pd.read_csv(f"../data/quality_comp/{f1}/{f2}/{s}.txt", header=None).values.flatten() - 3).tolist()
                strategies = [strats_translated[s] for item in items]
                strategies_tot += strategies
                items_tot += items
            df = pd.DataFrame(items_tot)
            df.columns = ["Number of Items Collected"]
            df["Strategy"] = strategies_tot

            title = ""
            match f1:
                case "mu":
                    title = f"m = 0.{f2.split('_')[1]}, s = 0.05, N = 25"
                case "sd":
                    title = f"m = 0.05, s = 0.{f2.split('_')[1]}, N = 25"
                case "popsize":
                    title = f"m = 0.05, s = 0.05, N = {f2.split('_')[1]}"

            sns.boxplot(data=df, x="Strategy", y="Number of Items Collected", linewidth=2, ax=axs[i])
            axs[i].set_title(title)
        plt.show()


def compare_behaviors():
    filenames = ["25careful", "25smart_t25",  # "25smart_t25",
                 "24careful_s3_1saboteur", "24smart_t25_1saboteur",  # "24smart_t25_1greedy",
                 "23careful_2saboteur", "23smart_t25_2saboteur",  # "23smart_t25_2greedy",
                 "22careful_3saboteur", "22smart_t25_3saboteur",  # "22smart_t25_3greedy",
                 "20careful_s3_5saboteur", "20smart_t25_5saboteur"  # , "20smart_t25_5greedy"
                 ]
    show_run_proportions(filenames, by=2)
    filenames = ["25honest", "25careful", "25smart_t25",
                 "24honest_1saboteur", "24careful_s3_1saboteur", "24smart_t25_1saboteur"]
    rewards_plot(filenames)
    show_run_proportions(filenames, by=3)
    filenames = [
        "25honest", "25smart_t10", "25smart_t25", "25smart_t40_0saboteur", "25smart_t100_0saboteur",
        "24honest_1saboteur", "24smart_t10_1saboteur", "24smart_t25_1saboteur", "24smart_t40_1saboteur",
        "24smart_t100_1saboteur"
    ]
    show_run_proportions(filenames, by=5)
    filenames = ["24smart_t25_1greedy", "24smart_t25_1greedy_minus10",
                 "22smart_t25_3greedy", "22smart_t25_3greedy_minus10",
                 "20smart_t25_5greedy", "20smart_t25_5greedy_minus10"]
    show_run_proportions(filenames, by=2)
    filenames = ["25honest", "25careful", "25smart_t25"]
    show_run_difference(filenames, by=3, metric="items_collected")
    filenames = ["24honest_1saboteur", "24careful_s3_1saboteur", "24smart_t25_1saboteur"]
    show_run_difference(filenames, by=3, metric="items_collected")


def powerpoint_plots():
    # filenames = ["24smart_t25_1greedy",
    #              "22smart_t25_3greedy",
    #              "20smart_t25_5greedy"]
    # # show_run_proportions(filenames, by=3)
    # make_violin_plots(filenames, by=3)
    # filenames = ["24smart_t25_1greedy_SoR_50",
    #              "22smart_t25_3greedy_SoR_50",
    #              "20smart_t25_5greedy_SoR_50"]
    # make_violin_plots(filenames, by=3, comparison_on="payment_types")
    # # show_run_proportions(filenames, by=3, comparison_on="payment_types")
    # filenames = ["24smart_t25_1saboteur",
    #              "22smart_t25_3saboteur",
    #              "20smart_t25_5saboteur"]
    # make_violin_plots(filenames, by=3)
    # # show_run_proportions(filenames, by=3)
    # filenames = ["24smart_t25_1saboteur_SoR_50",
    #              "22smart_t25_3saboteur_SoR_50",
    #              "20smart_t25_5saboteur_SoR_50"]
    # make_violin_plots(filenames, by=3, comparison_on="payment_types")
    # # show_run_proportions(filenames, by=3, comparison_on="payment_types")
    # filenames = ["24smart_t25_1smartboteur_SoR_50",
    #              "22smart_t25_3smartboteur_SoR_50",
    #              "20smart_t25_5smartboteur_SoR_50"]
    # make_violin_plots(filenames, by=3, comparison_on="saboteur_comp", title="Individual Share of Items Collected", metric="items_collected")
    # make_violin_plots(filenames, by=3, comparison_on="saboteur_comp", title="Individual Share of Total Reward")
    #
    # show_run_proportions(filenames, by=3, comparison_on="saboteur_comp")
    filenames = ["24smart_t25_1smartboteur_SoR_50_RTmarket",
                 "22smart_t25_3smartboteur_SoR_50_RTmarket",
                 "20smart_t25_5smartboteur_SoR_50_RTmarket"]
    make_violin_plots(filenames, by=3, comparison_on="saboteur_comp", title="Share of Reward based on Round-Trip Duration")
    # # show_run_proportions(filenames, by=3, comparison_on="saboteur_comp")
    # filenames = ["24smart_t25_1smartboteur_windowdev_50_fixedmarket",
    #              "22smart_t25_3smartboteur_windowdev_50_fixedmarket",
    #              "20smart_t25_5smartboteur_windowdev_50_fixedmarket"]
    # make_violin_plots(filenames, by=3, comparison_on="saboteur_comp", title="Window Filter Reward Share Transactions, Fixed Reward")
    #
    filenames = ["24smart_t25_1smartboteur_windowdev_50_RTmarket_bis",
                 "22smart_t25_3smartboteur_windowdev_50_RTmarket_bis",
                 "20smart_t25_5smartboteur_windowdev_50_RTmarket_bis"]
    make_violin_plots(filenames, by=3, comparison_on="saboteur_comp", title="Window Filter and Round-Trip Duration Reward")
    # show_run_proportions(filenames, by=3, comparison_on="saboteur_comp")
    # filenames = ["24smart_t25_1smartboteur_error^2dev_50_RTmarket",
    #              "22smart_t25_3smartboteur_error^2dev_50_RTmarket",
    #              "20smart_t25_5smartboteur_error^2dev_50_RTmarket"]
    # make_violin_plots(filenames, by=3, comparison_on="saboteur_comp", title="Square Error Filter Payment, Round Trip Market")
    # filenames = ["24smart_t25_1smartboteur_deltatime_50_RTmarket",
    #              "22smart_t25_3smartboteur_deltatime_50_RTmarket",
    #              "20smart_t25_5smartboteur_deltatime_50_RTmarket"]
    # make_violin_plots(filenames, by=3, comparison_on="saboteur_comp", title="Delta Time Payment, Round Trip Market")
    filenames = ["24smart_t25_1smartgreedy_windowdev_50_RTmarket",
                 "22smart_t25_3smartgreedy_windowdev_50_RTmarket",
                 "20smart_t25_5smartgreedy_windowdev_50_RTmarket"]
    make_violin_plots(filenames, by=3, comparison_on="saboteur_comp", title="Window Filter and Round-Trip Duration Reward")
    filenames = ["25honest_t25_1smartboteur_windowdev_50_RTmarket_bis",
                 "22smart_t25_3smartboteur_windowdev_50_RTmarket_bis"]

def compare_payment_types():
    filenames = []
    for i in [25, 24, 22, 20]:
        j = 25 - i
        filenames.append(f"{i}smart_t25_{j}greedy_50_infocost_fixed")
        filenames.append(f"{i}smart_t25_{j}greedy_50_infocost_timevarying")
    show_run_proportions(filenames, by=2, comparison_on="payment_types", metric="rewards")
    show_run_proportions([filenames[i] for i in [1, 3, 5, 7]], by=4, comparison_on="payment_types", metric="rewards")
    make_violin_plots([filenames[i] for i in [3, 5, 7]], by=3, comparison_on="payment_types", metric="rewards")


def compare_stop_time():
    filenames = []
    for i in [25, 23, 20]:
        j = 25 - i
        for cd in [10, 30, 60]:
            filenames.append(f"{i}smart_t25_{j}freerider_{cd}+10")
    show_run_proportions(filenames, by=3, comparison_on="stop_time", metric="rewards")


def honest_vs_careful():
    h_name = "24honest_1saboteur"
    c_name = "24careful_s3_1saboteur"
    hdf = pd.read_csv(f"../data/behaviors/rewards/{h_name}.txt", header=None)
    cdf = pd.read_csv(f"../data/behaviors/rewards/{c_name}.txt", header=None)
    hdiff = hdf.iloc[:, :24].apply(np.mean, axis=1) - hdf.iloc[:, 24]
    cdiff = cdf.iloc[:, :24].apply(np.mean, axis=1) - cdf.iloc[:, 24]
    fig, axs = plt.subplots()
    axs.set_title("Reward Difference with Saboteur")
    line_hist(hdiff.values.flatten(), 1.5)
    line_hist(cdiff.values.flatten(), 1.5)
    axs.legend(["honest", "careful"])
    plt.show()


def items_collected_plot(filenames):
    fig, axs = plt.subplots()
    for filename in filenames:
        collected = pd.read_csv(f"../data/behaviors/items_collected/{filename}.txt", header=None)
        n_honest = int(re.search('[0-9]+', filename).group())
        line_hist(collected.iloc[:, :n_honest].values.flatten(), 1)
    axs.legend(filenames)
    axs.set_title("Items Collected Distribution")
    plt.show()


def rewards_plot(filenames):
    fig, axs = plt.subplots()
    for filename in filenames:
        rewards = pd.read_csv(f"../data/behaviors/rewards/{filename}.txt", header=None)
        n_honest = int(re.search('[0-9]+', filename).group())
        line_hist(rewards.iloc[:, :n_honest].values.flatten(), 1)
    axs.legend(filenames)
    axs.set_title("Honest Rewards Distribution")
    plt.show()


def show_run_difference(filenames, by=1, comparison_on="behaviors", metric="rewards"):
    nrows = len(filenames) // by
    ncols = by
    fig, axs = plt.subplots(nrows=nrows, ncols=ncols, sharey=True, sharex=True)
    print(axs)
    fig.set_size_inches(4 * ncols, 6 * nrows)
    for i, filename in enumerate(filenames):
        row = i // by
        col = i % by
        df = pd.read_csv(f"../data/{comparison_on}/{metric}/{filename}.txt", header=None)
        n_honest = int(re.search('[0-9]+', filename).group())
        n_bad = 25 - n_honest

        if nrows == 1 or ncols == 1:
            frame = axs[row] if ncols == 1 else axs[col]
        else:
            frame = axs[row, col]

        frame.set_title(filename)
        frame.set_ylabel(metric)
        frame.set_xlabel("run")
        run_difference_plot(df, frame, n_bad, n_honest)
    plt.show()


def run_difference_plot(df, ax, n_bad, n_honest):
    means = df.iloc[:, :n_honest].apply(np.mean, axis=1)
    means_bad = df.iloc[:, -n_bad:].apply(np.mean, axis=1)
    stds = df.iloc[:, :n_honest].apply(np.std, axis=1)
    stds_bad = df.iloc[:, -n_bad:].apply(np.std, axis=1)
    res = pd.concat([means, stds, means_bad, stds_bad], axis=1, keys=['mean', 'sd', 'mean_b', 'sd_b'])
    res = res.sort_values(by='mean')
    ax.errorbar(range(res.shape[0]), res['mean'], res['sd'], linestyle='None', marker='^', c="tab:blue")
    if n_bad > 0:
        ax.errorbar(range(res.shape[0]), res['mean_b'], res['sd_b'], linestyle='None', marker='^',
                    c=(1, 0, 0, 1))


def show_run_proportions(filenames, by=1, comparison_on="behaviors", metric="rewards"):
    nrows = len(filenames) // by
    ncols = by
    fig, axs = plt.subplots(nrows=nrows, ncols=ncols, sharey=True, sharex=True)
    print(axs)
    fig.set_size_inches(4 * ncols, 6 * nrows)
    for i, filename in enumerate(filenames):
        row = i // by
        col = i % by
        df = pd.read_csv(f"../data/{comparison_on}/{metric}/{filename}.txt", header=None)
        n_honest = int(re.search('[0-9]+', filename).group())
        n_bad = 25 - n_honest
        honest_name = re.search('[a-z]+', filename.split("_")[0]).group()
        bad_name = ""
        if n_bad > 0:
            try:
                bad_name = re.search('[a-z]+', filename.split("_")[2]).group()
            except IndexError:
                bad_name = re.search('[a-z]+', filename.split("_")[1]).group()
        colors = {"smart": "blue", "honest": "blue", "careful": "blue",
                  "saboteur": "red",
                  "smartboteur": "red",
                  "greedy": "green"}
        if nrows == 1 and ncols == 1:
            frame = axs
        elif nrows == 1 or ncols == 1:
            frame = axs[row] if ncols == 1 else axs[col]
        else:
            frame = axs[row, col]

        totals = df.apply(np.sum, axis=1)
        frame.set_title(f"{filename}, throughput = {round(np.mean(totals))}")
        frame.set_ylabel(f"proportion of {metric} (%)")
        frame.set_xlabel("run")

        means = df.iloc[:, :n_honest].apply(np.mean, axis=1) * 100 / totals
        means_bad = df.iloc[:, -n_bad:].apply(np.mean, axis=1) * 100 / totals
        stds = df.iloc[:, :n_honest].apply(np.std, axis=1) * 100 / totals
        stds_bad = df.iloc[:, -n_bad:].apply(np.std, axis=1) * 100 / totals
        res = pd.concat([means, stds, means_bad, stds_bad], axis=1, keys=['mean', 'sd', 'mean_b', 'sd_b'])
        res = res.sort_values(by='mean')
        frame.errorbar(range(res.shape[0]), res['mean'], res['sd'], linestyle='None', marker='^', c=colors[honest_name])
        if n_bad > 0:
            frame.errorbar(range(res.shape[0]), res['mean_b'], res['sd_b'], linestyle='None', marker='^',
                           c=colors[bad_name])
    plt.show()


def rewards_per_run(filename):
    df = pd.read_csv(f"../data/behaviors/rewards/{filename}.txt", header=None)
    n_honest = int(re.search('[0-9]+', filename).group())
    fig, axs = plt.subplots()
    for row in range(df.shape[0]):
        values = df.iloc[row, :n_honest].values.flatten()
        bins = np.arange(np.floor(np.min(values)), np.ceil(np.max(values)), 1)
        # plt.hist(values, bins=bins, fc=(1, 0, 0, 0.1))
        line_hist(values, 1, 0.1, color=(0.5, 0, 0, 0.1))
    plt.show()


def line_hist(values, precision, alpha=1.0, color=None):
    bins = np.arange(np.floor(np.min(values)), np.ceil(np.max(values)), precision)
    n, bins = np.histogram(values, bins=bins, density=True)
    plt.plot(bins[:-1], n, alpha=alpha, c=color)


def supply_demand_simulation():
    n_bots = 25
    demand = 0.3
    max_price = 3
    creditor_share = 0.5
    static_rewards = []
    supplies = range(1, n_bots + 1)
    active_rewards = []
    active_only_rewards = []
    for supply in supplies:
        n_active = supply
        reward_per_active = exponential_model(demand=demand * n_bots, max_price=max_price, supply=supply)
        static_reward = n_active * (creditor_share / (n_bots - 1)) * reward_per_active
        static_rewards.append(static_reward)
        active_reward = (((n_active - 1) / (n_bots - 1) * creditor_share) + 1 - creditor_share) * reward_per_active
        active_rewards.append(active_reward)
        active_only_rewards.append((1 - creditor_share) * reward_per_active)
    plt.plot(supplies, static_rewards)
    plt.plot(supplies, active_only_rewards)
    plt.plot(supplies, active_rewards)
    plt.axhline(y=max(static_rewards), color='r', linestyle='-')
    plt.legend(
        ["information", "foraging", "information + foraging", f"information max ={round(max(static_rewards), 2)}"])
    plt.title(f"creditor share = {creditor_share}, demand = {demand}")
    plt.xlabel("supply")
    plt.ylabel("reward")
    plt.show()


def make_violin_plots(filenames, by=1, comparison_on="behaviors", metric="rewards",
                      title="Individual reward share across subpopulations"):
    nrows = len(filenames) // by
    ncols = by
    fig, axs = plt.subplots(nrows=nrows, ncols=1, sharey=True, sharex=True)
    fig.set_size_inches(3 * ncols, 6 * nrows)
    x_name = "Experiment"
    y_name = "Proportion of total wealth (%)"
    hue_name = "behavior"

    for row in range(nrows):
        row_df = pd.DataFrame(columns=[x_name, hue_name, y_name])
        if nrows == 1:
            frame = axs
        else:
            frame = axs[row]
        frame.set_title(title)
        for col in range(ncols):
            filename = filenames[row * ncols + col]
            df = pd.read_csv(f"../data/{comparison_on}/{metric}/{filename}.txt", header=None)
            n_honest = int(re.search('[0-9]+', filename).group())
            honest_name = re.search('[a-z]+', filename.split("_")[0]).group()
            honest_name = name_conversion[honest_name]
            bad_name = re.search('[a-z]+', filename.split("_")[2]).group()
            bad_name = name_conversion[bad_name]
            n_bad = 25 - n_honest

            totals = df.apply(np.sum, axis=1)
            # print(totals)
            df_rel = df.div(totals, axis=0) * 100
            # means = df.iloc[:, :n_honest].apply(np.mean, axis=1) * 100 / totals
            honest_flat = pd.DataFrame(df_rel.iloc[:, :n_honest].to_numpy().flatten())
            bad_flat = pd.DataFrame(df_rel.iloc[:, -n_bad:].to_numpy().flatten())
            print(filename, ranksums(honest_flat[:len(honest_flat)//15], honest_flat[len(honest_flat)//15:]))

            # means_bad = df.iloc[:, -n_bad:].apply(np.mean, axis=1) * 100 / totals
            # Draw a nested violinplot and split the violins for easier comparison

            goods = pd.DataFrame(np.full(honest_flat.shape, honest_name))
            bads = pd.DataFrame(np.full(honest_flat.shape, bad_name))
            honest_flat = pd.concat([honest_flat, goods], axis=1)
            bad_flat = pd.concat([bad_flat, bads], axis=1)
            final_df = pd.concat([honest_flat, bad_flat])
            final_df.columns = [y_name, hue_name]
            final_df[x_name] = f"{n_honest} {honest_name} vs {n_bad} {bad_name}"
            row_df = pd.concat([row_df, final_df])
        row_df.index = [i for i in range(row_df.shape[0])]
        temp = pd.DataFrame(row_df.to_dict())
        sns.violinplot(data=temp, x=x_name, y=y_name, hue=hue_name,
                       split=True, inner="quart", linewidth=2, ax=frame, palette=palette, cut=0)

    plt.show()

def make_boxplots(filenames, by=1, comparison_on="behaviors", metric="rewards",
                      title="Individual reward share across subpopulations"):
    nrows = len(filenames) // by
    ncols = by
    x_name = "Experiment"
    y_name = "Proportion of total wealth (%)"
    hue_name = "behavior"

    for row in range(nrows):
        fig, axs = plt.subplots(1, ncols, sharey=True)
        fig.suptitle(title)
        fig.supxlabel(x_name)
        fig.supylabel(y_name)
        fig.set_size_inches(3*ncols, 6)
        for col in range(ncols):
            filename = filenames[row * ncols + col]
            df = pd.read_csv(f"../data/{comparison_on}/{metric}/{filename}.txt", header=None)
            n_honest = int(re.search('[0-9]+', filename).group())
            honest_name = re.search('[a-z]+', filename.split("_")[0]).group()
            honest_name = name_conversion[honest_name]
            bad_name = re.search('[a-z]+', filename.split("_")[2]).group()
            bad_name = name_conversion[bad_name]
            n_bad = 25 - n_honest

            totals = df.apply(np.sum, axis=1)
            df_rel = df.div(totals, axis=0) * 100
            honest_flat = pd.DataFrame(df_rel.iloc[:, :n_honest].to_numpy().flatten())
            bad_flat = pd.DataFrame(df_rel.iloc[:, -n_bad:].to_numpy().flatten())
            print(filename, ranksums(honest_flat, bad_flat))

            goods = pd.DataFrame(np.full(honest_flat.shape, honest_name))
            bads = pd.DataFrame(np.full(honest_flat.shape, bad_name))
            honest_flat = pd.concat([honest_flat, goods], axis=1)
            bad_flat = pd.concat([bad_flat, bads], axis=1)
            final_df = pd.concat([honest_flat, bad_flat])
            final_df.columns = [y_name, hue_name]
            final_df[x_name] = f"{n_honest} {honest_name} vs {n_bad} {bad_name}"
            axs[col].set_title(chr(col+65), fontweight="bold")
            sns.boxplot(data=final_df, x=x_name, y=y_name, hue=hue_name, linewidth=2, ax=axs[col], palette=palette).set(xlabel=None, ylabel=None)
        plt.show()


def items_collected_violin_plot(df, frame, n_good, n_bad, good_name="naive", bad_name="saboteur", xlabel="all", title=None):

    honest_flat = pd.DataFrame(df.iloc[:, :n_good].to_numpy().flatten())
    bad_flat = pd.DataFrame(df.iloc[:, n_good:n_good+n_bad].to_numpy().flatten())

    goods = pd.DataFrame(np.full(honest_flat.shape, good_name))
    bads = pd.DataFrame(np.full(bad_flat.shape, bad_name))
    honest_flat = pd.concat([honest_flat, goods], axis=1)
    bad_flat = pd.concat([bad_flat, bads], axis=1)
    final_df = pd.concat([honest_flat, bad_flat])
    final_df.columns = ["items collected", "behavior"]
    final_df["run"] = xlabel
    split=n_bad > 0 and n_good > 0
    sns.violinplot(data=final_df, x="run", y="items collected", hue="behavior",
                   split=split, inner="quart", linewidth=2, ax=frame, palette=palette,
                   bw=0.275)
    if title:
        frame.set_title(title, fontweight="bold")
    frame.set(xlabel=None, ylabel=None)


def items_collected_boxplot(df, frame, n_good, n_bad, good_name="naive", bad_name="saboteur", xlabel="all", title=None):
    honest_flat = pd.DataFrame(df.iloc[:, :n_good].to_numpy().flatten())
    bad_flat = pd.DataFrame(df.iloc[:, n_good:n_good+n_bad].to_numpy().flatten())

    goods = pd.DataFrame(np.full(honest_flat.shape, good_name))
    bads = pd.DataFrame(np.full(bad_flat.shape, bad_name))
    honest_flat = pd.concat([honest_flat, goods], axis=1)
    bad_flat = pd.concat([bad_flat, bads], axis=1)
    final_df = pd.concat([honest_flat, bad_flat])
    final_df.columns = ["items collected", "behavior"]
    final_df["run"] = xlabel
    sns.boxplot(data=final_df, x="run", y="items collected", hue="behavior", linewidth=2,
                   ax=frame, palette=palette)
    if title:
        frame.set_title(title, fontweight="bold")
    frame.set(xlabel=None, ylabel=None)


def test_angles():
    df_all = pd.DataFrame([[1, 1, Location.FOOD, 0], [2, 4,Location.NEST, 0], [2, 5,Location.NEST, 0], [1, 100, Location.FOOD, 0], [4, 359,Location.FOOD, 0]], columns=["seller", "angle", "location", "alike"])
    angle_window = 5
    total_amount = 0.5
    for location in Location:
        df = df_all[df_all["location"] == location]
        df["alike"] = df.apply(func=lambda row: pd.DataFrame(
            [(df.iloc[:, 1] - row[1]) % 360,
             (row[1] - df.iloc[:, 1]) % 360]).
                               apply(min, axis=0).
                               sum(),
                               axis=1)
        # pd.DataFrame([(df.iloc[:, 1] - row[1]) % 360, (row[1] - df.iloc[:, 1]) % 360]).apply(min, axis=1).sum()
        # print(pd.DataFrame(
        #     [(df.iloc[:, 1] - df.iloc[1, 1]) % 360,
        #      (df.iloc[1, 1] - df.iloc[:, 1]) % 360]))
        # print(df)
        sellers_to_alike = df.groupby("seller").sum()
        print(sellers_to_alike)
        sellers_to_alike["alike"] = sellers_to_alike["alike"].sum() - sellers_to_alike["alike"]
        sellers_to_alike = sellers_to_alike.to_dict()["alike"]
        print(sellers_to_alike)
    # total_shares = sum(sellers_to_alike.values())
    # mapping = {seller: total_amount * sellers_to_alike[seller] / total_shares for seller in sellers_to_alike}
    # print(mapping)


def test_timedev():
    sorted_transactions = [[1, 1], [2, 4], [3, 4], [1, 7], [5, 12]]
    timestep = 20
    total_amount = 0.5
    sorted_transactions.append([-1, timestep])
    df = pd.DataFrame(sorted_transactions, columns=["seller", "time"])
    df["dt"] = df["time"].diff().shift(-1) + 1
    df = df[:-1]
    df["score"] = 1 / df["dt"]
    df["share"] = total_amount * df["score"] / df["score"].sum()
    mapping = df.groupby("seller").sum().to_dict()["share"]
    print(df)

    print(mapping)


def thesis_plots():
    # Chapter 8 - Section 1
    # chap8_1()

    # Chapter 8 - Section 2
    # chap8_2()

    # Chapter 9 - Section 1
    # filenames = ["24smart_t25_1smartboteur_SoR_50",
    #              "22smart_t25_3smartboteur_SoR_50",
    #              "20smart_t25_5smartboteur_SoR_50"]
    # make_violin_plots(filenames, by=3, comparison_on="saboteur_comp",
    #                   title="Wealth Repartition, Reward Share Transactions, Fixed Reward")
    # filenames = ["24smart_t25_1smartboteur_SoR_50_RTmarket",
    #              "22smart_t25_3smartboteur_SoR_50_RTmarket",
    #              "20smart_t25_5smartboteur_SoR_50_RTmarket"]
    # make_violin_plots(filenames, by=3, comparison_on="saboteur_comp",
    #                   title="Wealth Repartition, Reward Share Transactions, Round-trip Duration Reward")
    #
    # filenames = ["24smart_t25_1smartgreedy_windowdev_50_RTmarket",
    #              "22smart_t25_3smartgreedy_windowdev_50_RTmarket",
    #              "20smart_t25_5smartgreedy_windowdev_50_RTmarket"]
    # make_violin_plots(filenames, by=3, comparison_on="saboteur_comp",
    #                   title=" Wealth Repartition, Reward Share Transactions, Round-trip Duration Reward")
    #
    filenames = ["24smart_t25_1smartboteur_vouchwindowdev_50_fixedmarket",
                 "22smart_t25_3smartboteur_vouchwindowdev_50_fixedmarket",
                 "20smart_t25_5smartboteur_vouchwindowdev_50_fixedmarket"]
    make_violin_plots(filenames, by=3, comparison_on="saboteur_comp", metric="rewards",
                      title="Wealth Repartition, Window + Vouch, Fixed Reward")

    # Final Presentation

    # fig, axs = plt.subplots(1, 4, sharey=True)
    # fig.set_size_inches(12, 6)
    # fig.suptitle("Swarm Performance")
    # fig.supylabel("Number of Items Collected")
    # fig.supxlabel("Experiment")
    # df = pd.read_csv("../data/behaviors/items_collected/25honest.txt", header=None)
    # items_collected_violin_plot(df, axs[2], 25, 0, xlabel="25 naive")
    # df = pd.read_csv("../data/behaviors/items_collected/24honest_1saboteur.txt", header=None)
    # items_collected_violin_plot(df, axs[0], 24, 1, xlabel="24 naive vs 1 saboteur")
    # df = pd.read_csv("../data/behaviors/items_collected/25smart_t25.txt", header=None)
    # items_collected_violin_plot(df, axs[3], 25, 0, xlabel="25 smart", good_name="smart", bad_name="smartboteur")
    # df = pd.read_csv("../data/saboteur_comp/items_collected/24smart_t25_1smartboteur_SoR_50.txt", header=None)
    # items_collected_violin_plot(df, axs[1], 24, 1, xlabel="24 smart vs 1 smartboteur", good_name="smart", bad_name="smartboteur")
    # plt.show()
    #
    # fig, axs = plt.subplots(1, 3, sharey=True)
    # fig.set_size_inches(12, 6)
    # fig.suptitle("Swarm Performance")
    # fig.supylabel("Number of Items Collected")
    # fig.supxlabel("Experiment")
    # df = pd.read_csv("../data/saboteur_comp/items_collected/24smart_t25_1smartboteur_SoR_50.txt", header=None)
    # items_collected_violin_plot(df, axs[0], 24, 1, xlabel="24 smart vs 1 smartboteur")
    # df = pd.read_csv("../data/saboteur_comp/items_collected/22smart_t25_3smartboteur_SoR_50.txt", header=None)
    # items_collected_violin_plot(df, axs[1], 24, 1, xlabel="22 smart vs 3 smartboteur")
    # df = pd.read_csv("../data/saboteur_comp/items_collected/20smart_t25_5smartboteur_SoR_50.txt", header=None)
    # items_collected_violin_plot(df, axs[2], 24, 1, xlabel="20 smart vs 5 smartboteur")
    # plt.show()

    # df =pd.read_csv("../data/saboteur_comp/rewards/20smart_t25_5smartboteur_SoR_50_RTmarket.txt")
    # x = df.iloc[:, :20].to_numpy().flatten()
    # y = df.iloc[:, 20:].to_numpy().flatten()
    # res = mannwhitneyu(x, y, alternative='greater')
    # print(res)

    fig, axs = plt.subplots(1, 2, sharey=True)
    fig.set_size_inches(6, 6)
    fig.suptitle("Swarm Performance")
    fig.supylabel("Number of Items Collected")
    fig.supxlabel("Experiment")
    df = pd.read_csv("../data/saboteur_comp/items_collected/24smart_t25_1smartboteur_SoR_50.txt", header=None)
    items_collected_violin_plot(df, axs[0], 24, 1, xlabel="24 smart vs 1 smartboteur")
    df = pd.read_csv("../data/saboteur_comp/items_collected/24smart_t25_1smartboteur_vouchwindowdev_50_fixedmarket.txt", header=None)
    items_collected_violin_plot(df, axs[1], 24, 1, xlabel="24 smart vs 1 smartboteur")
    plt.show()




def chap8_2():
    filenames = ["../data/behaviors/items_collected/25honest.txt",
                 "../data/behaviors/items_collected/25smart_t25.txt",
                 "../data/behaviors/items_collected/25careful.txt"]
    robot_name = ["Naive", "Smart", "Careful"]
    fig, axs = plt.subplots(1, 3, sharey=True)
    fig.set_size_inches(10, 6)
    fig.suptitle("Comparing Honest Behaviors")
    fig.supylabel("Number of Items Collected")
    fig.supxlabel("Behavior")
    for i, file in enumerate(filenames):
        df = pd.read_csv(file, header=None)
        general_boxplot_data = df.values.flatten()
        sns.violinplot(x=[robot_name[i] for e in general_boxplot_data], y=general_boxplot_data, ax=axs[i], linewidth=2,
                       bw=.3)
    plt.show()
    robot_name = ["Smart", "Careful"]
    filenames = [
        "../data/saboteur_comp/items_collected/24smart_t25_1smartboteur_SoR_50.txt",
        "../data/saboteur_comp/items_collected/24smart_t25_1smartboteur_SoR_50_RTmarket.txt"]
    for i, file in enumerate(filenames):
        df = pd.read_csv(file, header=None)
        fig, axs = plt.subplots(1, 2, sharey=True)
        fig.suptitle(f"Performance of {robot_name[i]} Swarm with 1 Saboteur")
        fig.supylabel("Number of Items Collected")
        fig.supxlabel("Run Considered")
        print(np.median(df.to_numpy().flatten()))
        items_collected_violin_plot(df, axs[0], 24, 1, good_name=robot_name[i].lower())
        run_difference_plot(df, axs[1], 1, 24)
        plt.show()
    # x = pd.read_csv(filenames[0], header=None).to_numpy().flatten()
    # y = pd.read_csv(filenames[1], header=None).to_numpy().flatten()
    # print(len(x), len(y))
    # print(wilcoxon(x=x, y=y))


def chap8_1():
    filename = "../data/behaviors/items_collected/25honest.txt"
    df = pd.read_csv(filename, header=None)
    general_boxplot_data = df.values.flatten()
    fig, axs = plt.subplots(1, 2, sharey=True, gridspec_kw={'width_ratios': [1, 4]})
    fig.set_size_inches(10, 6)
    sns.violinplot(x=["all" for e in general_boxplot_data], y=general_boxplot_data, ax=axs[0], bw=.3, linewidth=2)
    run_difference_plot(df, axs[1], 0, 25)
    # run_difference_plot(pd.read_csv("../data/behaviors/items_collected/24honest_1saboteur.txt", header=None), axs[2], 1, 24)
    fig.suptitle("Performance of Naïve Swarm")
    fig.supylabel("Number of Items Collected")
    fig.supxlabel("Run Considered")
    plt.show()
    df = pd.read_csv("../data/behaviors/items_collected/24honest_1saboteur.txt", header=None)
    fig, axs = plt.subplots(1, 2, sharey=True, gridspec_kw={'width_ratios': [1, 4]})
    fig.set_size_inches(10, 6)
    fig.suptitle("Performance of Naïve Swarm with 1 Saboteur")
    fig.supylabel("Number of Items Collected")
    fig.supxlabel("Run Considered")
    items_collected_violin_plot(df, axs[0], 24, 1)
    run_difference_plot(df, axs[1], 1, 24)
    plt.show()


def test_windowdev():
    pd.options.mode.chained_assignment = None
    angle_window = 30
    total_amount = 0.5
    transactions = [[1, 1, Location.NEST, 0], [2, 4,Location.NEST, 0],
                    [2, 5, Location.NEST, 0], [3, 100, Location.NEST, 0],
                    [4, 359, Location.NEST, 0]]
    df_all = pd.DataFrame(transactions, columns=["seller", "angle", "location", "alike"])
    final_mapping = {}
    for location in Location:
        df = df_all[df_all["location"] == location]
        df.loc[:, "alike"] = df.apply(func=lambda row: (((df.loc[:, "angle"] - row[1]) % 360) < angle_window).sum()
                                                       + (((row[1] - df.loc[:, "angle"]) % 360) < angle_window).sum() - 1,
                                      axis=1)
        sellers_to_alike = df.groupby("seller").sum().to_dict()["alike"]
        mapping = {seller: sellers_to_alike[seller] for seller in sellers_to_alike}
        for seller in mapping:
            if seller in final_mapping:
                final_mapping[seller] += mapping[seller]
            else:
                final_mapping[seller] = mapping[seller]
    total_shares = sum(final_mapping.values())

    for seller in final_mapping:
        final_mapping[seller] = final_mapping[seller] * total_amount/total_shares
    print(final_mapping)


def test_np_windowdev():
    angle_window = 30
    total_amount = 0.5
    transactions = [[1, 1, Location.NEST, 0], [2, 4, Location.NEST, 0],
                    [2, 5, Location.NEST, 0], [3, 100, Location.NEST, 0],
                    [4, 359, Location.NEST, 0]]
    df_all = np.array(transactions)
    angle_window = 30
    final_mapping = {}
    for location in Location:
        df = df_all[df_all[:, 2] == location]
        if df.shape[0] == 0:
            continue
        df[:, 3] = np.apply_along_axis(func1d=lambda row: (((df[:, 1] - row[1]) % 360) < angle_window).sum()
                                                       + (((row[1] - df[:, 1]) % 360) < angle_window).sum() - 1,
                                    axis=1, arr=df)
        mapping = {seller: 0 for seller in df[:, 0]}
        for row in df:
            mapping[row[0]] += row[3]

        for seller in mapping:
            if seller in final_mapping:
                final_mapping[seller] += mapping[seller]
            else:
                final_mapping[seller] = mapping[seller]

    total_shares = sum(final_mapping.values())
    for seller in final_mapping:
        final_mapping[seller] = final_mapping[seller] * (total_amount) / total_shares
    print(final_mapping)

def paper_plots():
    sns.set_style("whitegrid")
    # fig, axs = plt.subplots(1, 4, sharey=True)
    # fig.set_size_inches(12, 6)
    # fig.suptitle("Swarm Performance")
    # fig.supylabel("Number of Items Collected")
    # fig.supxlabel("Experiment")
    #
    # df = pd.read_csv("../data/correlation/items_collected/25naive_0saboteur_nostake.txt", header=None)
    # items_collected_violin_plot(df, axs[0], 25, 0, xlabel="25 naive")
    #
    # df = pd.read_csv("../data/correlation/items_collected/24naive_1saboteur_nostake.txt", header=None)
    # items_collected_violin_plot(df, axs[1], 24, 1, xlabel="24 naive vs 1 saboteur")
    #
    # df = pd.read_csv("../data/correlation/items_collected/25smart_t25_0smartboteur_nostake.txt", header=None)
    # items_collected_violin_plot(df, axs[2], 25, 0, xlabel="25 sceptical", good_name="sceptical", bad_name="scaboteur")
    #
    # df = pd.read_csv("../data/correlation/items_collected/24smart_t25_1smartboteur_nostake.txt", header=None)
    # items_collected_violin_plot(df, axs[3], 24, 1, xlabel="24 sceptical vs 1 scaboteur", good_name="sceptical", bad_name="scaboteur")

    # df = pd.read_csv("../data/behaviors/items_collected/25smart_t25_0smartboteur_weighted.txt", header=None)
    # items_collected_violin_plot(df, axs[4], 25, 0, xlabel="25 smart weighted", good_name="smart", bad_name="smartboteur")
    #
    # df = pd.read_csv("../data/behaviors/items_collected/24smart_t25_1smartboteur_weighted.txt", header=None)
    # items_collected_violin_plot(df, axs[5], 24, 1, xlabel="24 smart vs 1 smartboteur weighted", good_name="smart",
    #                             bad_name="smartboteur")
    # plt.show ()

    fig, axs = plt.subplots(1, 4, sharey=True)
    fig.set_size_inches(12, 6)
    fig.suptitle("Swarm Performance")
    fig.supylabel("Number of Items Collected")
    fig.supxlabel("Experiment")
    df = pd.read_csv("../data/correlation/items_collected/25naive_0saboteur_nostake.txt", header=None)
    items_collected_boxplot(df, axs[0], 25, 0, xlabel="25 naive", title="A")

    df = pd.read_csv("../data/correlation/items_collected/24naive_1saboteur_nostake.txt", header=None)
    items_collected_boxplot(df, axs[1], 24, 1, xlabel="24 naive vs 1 saboteur", title="B")

    df = pd.read_csv("../data/correlation/items_collected/25smart_t25_0smartboteur_nostake.txt", header=None)
    items_collected_boxplot(df, axs[2], 25, 0, xlabel="25 sceptical", good_name="sceptical", bad_name="scaboteur", title="C")

    df = pd.read_csv("../data/correlation/items_collected/24smart_t25_1smartboteur_nostake.txt", header=None)
    items_collected_boxplot(df, axs[3], 24, 1, xlabel="24 sceptical vs 1 scaboteur", good_name="sceptical",
                                bad_name="scaboteur", title="D")

    # df = pd.read_csv("../data/behaviors/items_collected/25smart_t25_0smartboteur_weighted.txt", header=None)
    # items_collected_boxplot(df, axs[4], 25, 0, xlabel="25 smart weighted", good_name="smart",
    #                             bad_name="scaboteur")
    #
    # df = pd.read_csv("../data/behaviors/items_collected/24smart_t25_1smartboteur_weighted.txt", header=None)
    # items_collected_boxplot(df, axs[5], 24, 1, xlabel="24 smart vs 1 smartboteur weighted", good_name="smart",
    #                             bad_name="smartboteur")
    plt.show()

    filenames = ["24smart_t25_1smartboteur_nostake",
                 "22smart_t25_3smartboteur_nostake",
                 "20smart_t25_5smartboteur_nostake"]
    # make_violin_plots(filenames, by=3, comparison_on="correlation", title="Wealth Repartition - Outlier Penalisation")
    make_boxplots(filenames, by=3, comparison_on="correlation",
                      title="Wealth Repartition - Outlier Penalisation")

    filenames = ["24smart_t25_1smartboteur_windowvouch",
                 "22smart_t25_3smartboteur_windowvouch",
                 "20smart_t25_5smartboteur_windowvouch"]
    # make_violin_plots(filenames, by=3, comparison_on="correlation", metric="rewards", title="Wealth Repartition - Outlier Penalisation with Staking")
    make_boxplots(filenames, by=3, comparison_on="correlation", metric="rewards",
                      title="Wealth Repartition - Outlier Penalisation with Staking")


def to_reward_wealth_proportion(df):
    totals = df.apply(np.sum, axis=1)
    df_rel = df.div(totals, axis=0) * 100
    return df_rel


def to_long(df, N_HONEST, x_name, y_name, hue_name, honest_name, saboteur_name):
    df.columns = [str(i + 1) for i in range(25)]
    df[x_name] = df.index
    df = pd.melt(df, id_vars=[x_name], value_vars=[str(i + 1) for i in range(25)], var_name="id", value_name=y_name)
    df[hue_name] = honest_name
    df.loc[df["id"].astype(int) > N_HONEST, hue_name] = saboteur_name
    return df


def reward_evolution():
    N_RUNS = 32
    N_HONEST = 20
    N_SABOTEURS = 25-N_HONEST
    x_name = "time"
    y_name = "Individual weatlh ($)"
    hue_name = "behavior"
    honest_name = "sceptical"
    saboteur_name = "scaboteur"
    dfs = []
    for i in range(N_RUNS):
        df = pd.read_csv(f"../data/correlation/reward_evolution/{N_HONEST}smart_t25_{N_SABOTEURS}smartboteur_nostake/{i}.txt", header=None, index_col=0)
        # df = to_reward_wealth_proportion(df)
        df = df.iloc[::10, :]
        df = to_long(df, N_HONEST, x_name, y_name, hue_name, honest_name, saboteur_name)
        dfs.append(df)
    df = pd.concat(dfs, ignore_index=True)
    print(df)
    plt.suptitle("A", fontweight="bold")
    plt.title(f"Outlier penalisation - {N_HONEST} {honest_name} vs {N_SABOTEURS} {saboteur_name}")
    sns.lineplot(data=df, x=x_name, y=y_name, hue=hue_name, palette=palette)
    plt.show()


def correlation_plot(filename, directory, suptitle=None):
    n_honest = int(re.search('[0-9]+', filename).group())
    n_bad = 25 - n_honest
    honest_name = re.search('[a-z]+', filename.split("_")[0]).group()
    bad_name = re.search('[a-z]+', filename.split("_")[2]).group()
    rewards = pd.read_csv(f"{directory}rewards/{filename}", header=None)
    items_collected = pd.read_csv(f"{directory}items_collected/{filename}", header=None)
    # rewards = rewards - 0.5*items_collected
    wealth = to_reward_wealth_proportion(rewards)
    drifts = pd.read_csv(f"{directory}drifts/{filename}", header=None)
    drifts = drifts.applymap(abs)
    y = wealth.iloc[:, :n_honest].to_numpy().flatten()
    x = drifts.iloc[:, :n_honest].to_numpy().flatten()
    sns.regplot(x=x, y=y, scatter=True, truncate=True,
                line_kws={"color":"darkblue"}, scatter_kws={"alpha":0.2, "linewidth":0})
    plt.title(f"{n_honest} sceptical vs {n_bad} scaboteurs with staking")  #- pearson={round(np.corrcoef(x, y)[0, 1], 2)}
    plt.xlabel("drift")
    plt.ylabel("Proportion of total wealth(%)")
    if suptitle:
        plt.suptitle(suptitle, fontweight="bold")
    plt.show()

filenames = [
    "25smart_t25_0smartboteur_windowvouch.txt",
    "20smart_t25_5smartboteur_windowvouch.txt",
    # "22smart_t25_3smartboteur_windowvouch.txt",
    # "24smart_t25_1smartboteur_windowvouch.txt",
]
def correlation_plots():
    for i, filename in enumerate(filenames):
        correlation_plot(filename, "../data/correlation/", chr(i+65))

if __name__ == '__main__':
    # supply_demand_simulation()
    # compare_behaviors()
    # compare_payment_types()
    # compare_stop_time()
    # show_run_proportions(["20smart_t25_5freerider_10+10"], comparison_on="stop_time")
    # make_violin_plots(["20smart_t25_5saboteur", "22smart_t25_3saboteur"], by=2)
    # powerpoint_plots()
    # time = perf_counter()
    # for i in range(1):
    #     test_windowdev()
    # dt1 = perf_counter()-time
    # time = perf_counter()
    # for i in range(1):
    #     test_np_windowdev()
    # dt2 = perf_counter()-time
    # print(f"pd: {dt1}, np:{dt2}")
    # test_timedev()
    # thesis_plots()
    # compare_strats()
    # paper_plots()
    reward_evolution()
    # correlation_plots()
