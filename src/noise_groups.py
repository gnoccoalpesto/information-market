def id_list1(n_robots,
            n_dishonest,
            dishonest_noise_performance,
            noise_mu=.051, noise_range=0.1,
            ):
    
    if dishonest_noise_performance=="avg":
        rounded_n_honests=n_robots//2-2
        generation_list=[_ for _ in [_ for _ in range(rounded_n_honests)]+
                                    [_ for _ in range(rounded_n_honests+n_dishonest,n_robots)]+
                                    [_ for _ in range(rounded_n_honests,rounded_n_honests+n_dishonest)]]
    elif dishonest_noise_performance=="perf":
        ids_negative_value_dict={"0.1":int(200*(0.05-noise_mu)),
                                "0.15":n_robots//7,
                                "0.2":n_robots//5}
        try:    
            ids_negative_value=ids_negative_value_dict[str(noise_range)]
        except KeyError:
            if noise_range>0.1 and noise_range<0.15:
                ids_negative_value=int((ids_negative_value_dict["0.15"]+ids_negative_value_dict["0.1"])//2)
            elif noise_range>0.15 and noise_range<0.2:
                ids_negative_value=int((ids_negative_value_dict["0.2"]+ids_negative_value_dict["0.15"])//2)
            elif noise_range>0.2:
                ids_negative_value=n_robots//3

        "eg 6robots, 2 d: 0,1,2,3,4,5,6"
        generation_list=[_ for _ in [_ for _ in range(ids_negative_value)]+
                                    [_ for _ in range(ids_negative_value+n_dishonest,n_robots)]+
                                    [_ for _ in range(ids_negative_value,ids_negative_value+n_dishonest)]]

    print(generation_list)    


def id_list2(n_robots,
             n_dishonest,
             saboteur_performance):
    n_honest=n_robots-n_dishonest

    if saboteur_performance=="avg":
        good_slice=n_honest//2+(1 if n_dishonest==0 else 0)
    elif saboteur_performance=="perf":
        good_slice=n_robots//2-n_dishonest+1
    bad_slice=-n_dishonest if n_dishonest>0 else n_robots-n_dishonest
    print(good_slice,bad_slice)

# id_list1(25,7,"perf")
id_list2(25,2,"perf")