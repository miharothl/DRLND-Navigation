import os
from datetime import datetime

import gym
# !pip3 install box2d
import random
import torch
import numpy as np
from collections import deque
import matplotlib.pyplot as plt
# %matplotlib inline

# !python -m pip install pyvirtualdisplay
from pyvirtualdisplay import Display

class Train:
    def __init__(self, model_id, path_models='models'):
        self.__model_id = model_id
        self.__timestamp = self.get_timestamp()
        self.__path_models = path_models

    def plot(self, scores):
        # plot the scores
        fig = plt.figure()
        ax = fig.add_subplot(111)
        plt.plot(np.arange(len(scores)), scores)
        plt.ylabel('Score')
        plt.xlabel('Episode #')
        plt.show()

    def get_timestamp(self):
        # return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        return datetime.now().strftime("%Y%m%dT%H%M")

    def get_model_filename(self, episode, score, eps):
        import re
        model_id = re.sub('[^0-9a-zA-Z]+', '', self.__model_id)
        model_id = model_id.lower()
        filename = "{}_{}_{}_{:.2f}_{:.2f}.pth".format(model_id, self.__timestamp, episode, score, eps)
        return os.path.join(self.__path_models, filename)

    def dqn(self, agent, env, n_episodes=3000, max_t=1000, eps_start=1.0, eps_end=0.01, eps_decay=0.997, terminate_soore=300.0):
        """Deep Q-Learning.

        Params
        ======
            n_episodes (int): maximum number of training episodes
            max_t (int): maximum number of timesteps per episode
            eps_start (float): starting value of epsilon, for epsilon-greedy action selection
            eps_end (float): minimum value of epsilon
            eps_decay (float): multiplicative factor (per episode) for decreasing epsilon
        """
        scores = []                        # list containing scores from each episode
        scores_window = deque(maxlen=100)  # last 100 scores
        eps = eps_start                    # initialize epsilon
        for i_episode in range(1, n_episodes+1):
            state = env.reset()
            score = 0
            for t in range(max_t):
                action = agent.act(state, eps)
                next_state, reward, done, _ = env.step(action)
                agent.step(state, action, reward, next_state, done)
                state = next_state
                score += reward
                if done:
                    break
            scores_window.append(score)       # save most recent score
            scores.append(score)              # save most recent score

            eps = max(eps_end, eps_decay*eps) # decrease epsilon

            model_filename = self.get_model_filename(i_episode, np.mean(scores_window), eps)

            print('\rEpisode {}\tAverage Score: {:.2f}\tEpsilon: {:.2f}'.format(i_episode, np.mean(scores_window), eps), end="")
            if i_episode % 100 == 0:
                print('\rEpisode {}\tAverage Score: {:.2f}\tEpsilon: {:.2f}'.format(i_episode, np.mean(scores_window), eps))
                self.plot(scores)
                torch.save(agent.qnetwork_local.state_dict(), model_filename)

            if np.mean(scores_window)>=terminate_soore:
                print('\nEpisode {}\tAverage Score: {:.2f}\tEpsilon: {:.2f}'.format(i_episode-100, np.mean(scores_window), eps))
                torch.save(agent.qnetwork_local.state_dict(), model_filename)
                break

        return scores

