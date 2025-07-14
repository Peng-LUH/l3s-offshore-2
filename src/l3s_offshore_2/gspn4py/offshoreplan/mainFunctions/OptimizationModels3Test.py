import numpy as np
import gurobipy as gp
from gurobipy import GRB
from utils.hours import hours

def generate_plan(expectedDuration, scenario):
    # Sets up the optimizer and runs it.
    # Input:
    #   expectedDuration: integer(4xN) 1: Build OWT, 2: MoveToPort,
    #                     3: MoveToSite, 4: PortOperations
    #   Scenario: Struct

    # Initialize Gurobi model
    m = gp.Model("OWT_Planning")

    # Make sure these are integers
    expectedDuration = np.round(expectedDuration)

    N = scenario.N
    vI = scenario.numInstallationVessels

    benefit = scenario.benefitForFinishingAnOWT
    benefitEarly = scenario.maxBenefitForFinishingEarly
    modV = 0.05 * np.arange(vI)

    # Decision Variables
    location = m.addVars(vI, N, vtype=GRB.INTEGER, name="location")
    capacity = m.addVars(vI, N, vtype=GRB.INTEGER, name="capacity")
    xOWT = m.addVars(vI, N, vtype=GRB.INTEGER, name="xOWT")
    xPortOp = m.addVars(vI, N, vtype=GRB.INTEGER, name="xPortOp")
    xToPort = m.addVars(vI, N, vtype=GRB.INTEGER, name="xToPort")
    xToSite = m.addVars(vI, N, vtype=GRB.INTEGER, name="xToSite")
    xBusy = m.addVars(vI, N, vtype=GRB.INTEGER, name="xBusy")
    xPortOpD = m.addVars(vI, N, vtype=GRB.INTEGER, name="xPortOpD")
    xOWT_TimeFinished = m.addVars(vI, N, vtype=GRB.INTEGER, name="xOWT_TimeFinished")
    xMinorOps_TimeFinished = m.addVars(vI, N, vtype=GRB.INTEGER, name="xMinorOps_TimeFinished")
    xPortRestockOp = m.addVars(N, vtype=GRB.INTEGER, name="xPortRestockOp")
    xPortCapacity = m.addVars(N, vtype=GRB.INTEGER, name="xPortCapacity")
    cost = m.addVar(vtype=GRB.CONTINUOUS, name="cost")

    dur_Movement = scenario.opData[0, 6]



    # Add the cost expression to the objective function
    m.addConstr(
        cost == gp.quicksum(location[v, k] * (scenario.costOffshore + modV[v]) for v in range(vI) for k in range(N)) +
        gp.quicksum(xPortOpD[v, k] * (scenario.costPortOp + modV[v]) for v in range(vI) for k in range(N)) +
        gp.quicksum(xToSite[v, k] * (scenario.costFuel * dur_Movement + modV[v]) for v in range(vI) for k in range(N)) +
        gp.quicksum(xToPort[v, k] * (scenario.costFuel * dur_Movement + modV[v]) for v in range(vI) for k in range(N)) +
        (gp.quicksum(xPortCapacity[k] for k in range(N)) / (N * scenario.maximumPortCapacity)) * scenario.storagePenalty -
        gp.quicksum(xOWT[v, k] * benefit for v in range(vI) for k in range(N)) -
        gp.quicksum((N - xOWT_TimeFinished[v, k]) / N * benefitEarly for v in range(vI) for k in range(N)) -
        gp.quicksum((N - xMinorOps_TimeFinished[v, k]) / N * ((benefitEarly * 0.2) / N / 84) for v in range(vI) for k in range(N)) +
        gp.quicksum(xPortOpD[v, k] for v in range(vI) for k in range(N)) * 0.01 
        )


    # Set up the objective function
    m.setObjective(
        cost,
        GRB.MINIMIZE
        )
    
    # Constraints

    # Capacity
    constr_capacityMax = m.addConstrs((capacity[v, k] <= scenario.maxShipCapacities[v] for v in range(vI) for k in range(N)),
                                       name="constr_capacityMax")
    constr_capacity = m.addConstrs((capacity[v, k] == capacity[v, k - 1] - xOWT[v, k] + xPortOp[v, k] if k > 0 else
                                     capacity[v, k] == scenario.currentCapacity[v] - xOWT[v, k] + xPortOp[v, k]
                                     for v in range(vI) for k in range(N)), name="constr_capacity")

    # Only one task at a time
    constr_oneJob = m.addConstrs((xOWT[v, k] + xToPort[v, k] + xToSite[v, k] + xPortOp[v, k] + xBusy[v, k] <= 1
                                   for v in range(vI) for k in range(N)), name="constr_oneJob")

    # Record Build times
    constr_finishTimes = m.addConstrs((xOWT_TimeFinished[v, k] == xOWT[v, k] * (k + expectedDuration[0, k] - 1)
                                        for v in range(vI) for k in range(N)), name="constr_finishTimes")
    constr_finishOps = m.addConstrs((
        xMinorOps_TimeFinished[v, k] == xPortOp[v, k] * (k + expectedDuration[3, k] - 1) +
        xToPort[v, k] * (k + expectedDuration[2, k] - 1) +
        xToSite[v, k] * (k + expectedDuration[1, k] - 1)
        for v in range(vI) for k in range(N)), name="constr_finishOps")

    # Define location
    constr_location1 = m.addConstrs((location[v, k] == location[v, k - 1] - (xToPort[v, k]) + xToSite[v, k] if k > 0 else
                                      location[v, k] == scenario.currentLocation[v] - (xToPort[v, k]) + xToSite[v, k]
                                      for v in range(vI) for k in range(N)), name="constr_location1")
    constr_location2 = m.addConstrs((location[v, k] >= xOWT[v, k] for v in range(vI) for k in range(N)),
                                     name="constr_location2")
    constr_location3 = m.addConstrs((location[v, k] <= (1 - xPortOp[v, k]) for v in range(vI) for k in range(N)),
                                     name="constr_location3")

    # Don't build more than required
    constr_maxOWT = m.addConstr(gp.quicksum(gp.quicksum(xOWT[v, k] for v in range(vI)) for k in range(N)) <= scenario.OWTsToBuild - scenario.BuiltOWTs,
                                    name="constr_maxOWT")

    # Durations
    constr_duration_owt = m.addConstrs( (gp.quicksum(xBusy[v, n] for n in range(k+1, min(k + int(expectedDuration[0, k])-1, N) ) ) >= xOWT[v, k] *
                                        int(expectedDuration[0, k]) for v in range(vI) for k in range(N)),
                                       name="constr_duration_owt")
    
    constr_duration_move = m.addConstrs((gp.quicksum(xBusy[v, n] for n in range(k+1, min(k + int(expectedDuration[1, k])-1, N) ) ) >=
                                          (xToPort[v, k] + xToSite[v, k]) * int(expectedDuration[1, k])
                                          for v in range(vI) for k in range(N)), name="constr_duration_move")
    
    constr_duration_port = m.addConstrs((gp.quicksum(xBusy[v, n] for n in range(k+1, min(k + int(expectedDuration[3, k])-1, N) ) ) >= xPortOp[v, k] *
                                          int(expectedDuration[3, k]) for v in range(vI) for k in range(N)),
                                        name="constr_duration_port")
    
    constr_durationPort_port = m.addConstrs((gp.quicksum(xPortOpD[v, n] for n in range(k, min(k + int(expectedDuration[3, k])-1, N) ) ) >= xPortOp[v, k] *
                                          (int(expectedDuration[3, k])+1 ) for v in range(vI) for k in range(N)),
                                        name="constr_duration_port")
    
    constr_finish = m.addConstrs((xOWT[v, k] <= max(0, (N - k) - (int(expectedDuration[0, k]) - 1))
                                  for v in range(vI) for k in range(N)), name="constr_finish")

    # Vessel start times
    constr_vesselStart = m.addConstrs(
        (xOWT[v, k] + xToPort[v, k] + xToSite[v, k] + xPortOp[v, k] + xBusy[v, k] == 0
         for v in range(vI) for k in range(N) if k - hours(scenario.vesselStart[v]-scenario.currentDate) <= 0), name="constr_vesselStart")

    # Loading Bays in Port
    #constr_bays = m.addConstrs((gp.quicksum(xPortOpD[v, k] for v in range(vI)) + scenario.blockedBays[k] <=
    #                             scenario.numLoadingBaysInPort for k in range(N)), name="constr_bays")

    # PORT CAPACITY
    constr_pCapacityStart = m.addConstr(
        (xPortCapacity[0] <= scenario.currentPortCapacity - gp.quicksum(xPortOp[v, 0] for v in range(vI)) +
         (xPortRestockOp[0] * scenario.portRestockAmount) - scenario.scheduledLoadingOps[0]),
        name="constr_pCapacityStart")
    
    constr_pCapacity = m.addConstrs((xPortCapacity[k] == xPortCapacity[k - 1] - gp.quicksum(xPortOp[v, k] for v in range(vI)) +
                                     (xPortRestockOp[k] * scenario.portRestockAmount) -
                                     scenario.scheduledLoadingOps[k]
                                     for k in range(1, N)), name="constr_pCapacity")
    
    constr_pCapactyFreq = m.addConstrs(
        (gp.quicksum(xPortRestockOp[n] for n in range(max(0, k - scenario.portRestockFrequency), k)) <= 1 for k in range(N)),
        name="constr_pCapactyFreq")
    
    if scenario.portRestockEarliest > 1:
        block = min(scenario.portRestockEarliest, N)
        constr_pCapactyBlock = m.addConstr(
            (gp.quicksum(xPortRestockOp[n] for n in range(block)) == 0), name="constr_pCapactyBlock")

    m.optimize()

    # Retrieve solution


    solution.location_values = np.zeros((vI, N))
    solution.capacity_values = np.zeros((vI, N))
    solution.xOWT_values = np.zeros((vI, N))



    for i in range(vI):
        for j in range(N):
            solution.location[i, j] = location[i, j].x
            solution.capacity[i, j] = capacity[i, j].x
            solution.xOWT[i, j] = xOWT[i, j].x
            # Store values for other variables as well


    solution.xPortRestockOp = np.zeros(N)
    solution.xPortCapacity = np.zeros(N)
        
    for j in range(N):
        xPortRestockOp_values[j] = xPortRestockOp[j].x
        xPortCapacity_values[j] = xPortCapacity[j].x

    solution.cost = cost.x

# Now you have NumPy arrays containing the values of each decision variable


    return solution, m.status

# Note: You need to define the scenario and expectedDuration appropriately in the Python environment.
