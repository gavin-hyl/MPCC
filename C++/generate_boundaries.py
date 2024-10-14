import json
import numpy as np
import matplotlib.pyplot as plt

TRAJ_FILE = 'monza_trajectory.json'   # there was a nan point, and I removed it *by hand*
TRACK_WIDTH = 11    # https://www.monzanet.it/en/circuit/
# TRAJ_FILE = 'kentucky_trajectory.json'
# TRACK_WIDTH = 18    # https://www.kentuckyspeedway.com/media/facts/

def main():
    with open(f"Params/{TRAJ_FILE}") as f:
        data = json.load(f)
        X_center = data['X']
        Y_center = data['Y']
        X_center.append(X_center[0])    # close the loop
        Y_center.append(Y_center[0])
        X_center = np.array(X_center) - X_center[0]
        Y_center = np.array(Y_center) - Y_center[0]

    # sometimes the centerline has duplicate points, remove them to avoid normalization issues
    X_center_no_dup = []
    Y_center_no_dup = []
    for x, y in zip(X_center, Y_center):
        x_duplicated = False
        y_duplicated = False
        for x_dup in X_center_no_dup:
            if abs(x - x_dup) < 1e-6:
                x_duplicated = True
                break
        for y_dup in Y_center_no_dup:
            if abs(y - y_dup) < 1e-6:
                y_duplicated = True
                break
        if x_duplicated and y_duplicated:
            continue
        X_center_no_dup.append(x)
        Y_center_no_dup.append(y)
    
    scale = 3 / (np.max(X_center) - np.min(X_center))   # scale the track to fit the 1:43 RC car parameters, TEMP FIX
    scale = 1 / 43   # set to 1 for the real scale, doesn't work well with the current MPCC setup
    X_center_no_dup = np.array(X_center_no_dup) * scale
    Y_center_no_dup = np.array(Y_center_no_dup) * scale

    dx = np.diff(X_center_no_dup)[:-1]
    dy = np.diff(Y_center_no_dup)[:-1]
    normal = np.array([dy, -dx]) / np.sqrt(dx**2 + dy**2)
    outer_track = np.array([X_center_no_dup[:-2], Y_center_no_dup[:-2]]) + TRACK_WIDTH / 2 * normal * scale
    inner_track = np.array([X_center_no_dup[:-2], Y_center_no_dup[:-2]]) - TRACK_WIDTH / 2 * normal * scale
    outer_track = np.hstack((outer_track, outer_track[:, [0]]))
    inner_track = np.hstack((inner_track, inner_track[:, [0]]))

    print(f"Track width: {TRACK_WIDTH * scale}m")

    plot = True
    if plot:
        plt.plot(X_center_no_dup, Y_center_no_dup, label="X vs Y (vehicle path)")
        plt.plot(inner_track[0], inner_track[1], label="Inner Track (X_i vs Y_i)")
        plt.plot(outer_track[0], outer_track[1], label="Outer Track (X_o vs Y_o)")
        plt.axis('equal')
        plt.xlabel("X")
        plt.ylabel("Y")
        plt.hlines(0, -0.5, 0.5, colors='gray', linestyles='dashed')
        plt.vlines(0, -0.5, 0.5, colors='gray', linestyles='dashed')
        plt.legend()
        plt.title("Mini Track")
        plt.show()

    output_data = {
        'X': X_center_no_dup[:-1].tolist(),
        'Y': Y_center_no_dup[:-1].tolist(),
        'X_i': inner_track[0].tolist(),
        'Y_i': inner_track[1].tolist(),
        'X_o': outer_track[0].tolist(),
        'Y_o': outer_track[1].tolist(),
    }
    with open(f"Params/mini_{TRAJ_FILE}", "w") as f:
        json.dump(output_data, f)

if __name__ == '__main__':
    main()