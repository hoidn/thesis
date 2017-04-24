import pdb
import numpy as np

def rotation_matrix(axis, theta):
    """
    Return the rotation matrix associated with counterclockwise rotation about
    the given axis by theta radians.
    """
    axis = np.asarray(axis)
    axis = axis/math.sqrt(np.dot(axis, axis))
    a = math.cos(theta/2.0)
    b, c, d = -axis*math.sin(theta/2.0)
    aa, bb, cc, dd = a*a, b*b, c*c, d*d
    bc, ad, ac, ab, bd, cd = b*c, a*d, a*c, a*b, b*d, c*d
    return np.array([[aa+bb-cc-dd, 2*(bc+ad), 2*(bd-ac)],
                     [2*(bc-ad), aa+cc-bb-dd, 2*(cd+ab)],
                     [2*(bd+ac), 2*(cd-ab), aa+dd-bb-cc]])

def rand_vec():
    return np.random.uniform(-1, 1, size = 3)

def random_orthogonal(axis):
    rand0 = rand_vec()
    orthog = rand0 - (np.dot(rand0, axis)/np.dot(axis, axis)) * axis
    return orthog/np.linalg.norm(orthog)

def simulate_elastic_scattering(csda = 1., elastic_mfp = 0.1, characteristic_angle = 0.1):
    track = []
    direction = np.array([1., 0., 0.])
    position = np.array([0., 0., 0.])
    tot_distance = 0.
    delta_magnitude = np.tan(characteristic_angle)
    pdb.set_trace()
    while tot_distance < csda:
        track.append(position.copy())
        position_increment = (np.random.exponential(elastic_mfp) * direction)
        position += position_increment
        direction_increment = random_orthogonal(direction) * delta_magnitude
        print(direction_increment)
        print(direction)
        direction += direction_increment
        direction /= np.linalg.norm(direction)
        tot_distance += np.linalg.norm(position_increment)
    return track

#def simulate_track(elastic_mfp, characteristic_angle, stopping_length):
