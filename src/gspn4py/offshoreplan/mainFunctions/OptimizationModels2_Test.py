import numpy as np
from gurobipy import Model, GRB
import gurobipy as gp
from utils.hours import hours
from utils.printMsg import printMsg

def generate_plan(expectedDuration, scenario):
    
    # Settings and costs
    N = scenario.N
    vI = scenario.numInstallationVessels

    benefit = scenario.benefitForFinishingAnOWT
    benefitEarly = scenario.maxBenefitForFinishingEarly
    modV = 0.05 * np.arange(vI)
    dur_Movement = scenario.opData[0,6];
    

    # Create a new GUROBI model
    model = Model("installation_plan")

    # Decision variables
    location = model.addVars(vI, N, vtype=GRB.INTEGER, lb=0, ub=1, name="location")
    capacity = model.addVars(vI, N, vtype=GRB.INTEGER, lb=0, name="capacity")
    xOWT = model.addVars(vI, N, vtype=GRB.INTEGER, lb=0, ub=1, name="xOWT")
    xPortOp = model.addVars(vI, N, vtype=GRB.INTEGER, lb=0, ub=1, name="xPortOp")
    xToPort = model.addVars(vI, N, vtype=GRB.INTEGER, lb=0, ub=1, name="xToPort")
    xToSite = model.addVars(vI, N, vtype=GRB.INTEGER, lb=0, ub=1, name="xToSite")
    xBusy = model.addVars(vI, N, vtype=GRB.INTEGER, lb=0, ub=1, name="xBusy")
    xPortOpD = model.addVars(vI, N, vtype=GRB.INTEGER, lb=0, ub=1, name="xPortOpD")
    xOWT_TimeFinished = model.addVars(vI, N, vtype=GRB.INTEGER, lb=0, name="xOWT_TimeFinished")
    xMinorOps_TimeFinished = model.addVars(vI, N, vtype=GRB.INTEGER, lb=0, name="xMinorOps_TimeFinished")
    xPortRestockOp = model.addVars(N, vtype=GRB.INTEGER, lb=0, ub=1, name="xPortRestockOp")
    xPortCapacity = model.addVars(N, vtype=GRB.INTEGER, lb=0, ub=scenario.maximumPortCapacity, name="xPortCapacity")
    cost = model.addVar(vtype=GRB.CONTINUOUS, name="cost")

    # Objective function
    model.setObjective(
        gp.quicksum(gp.quicksum(location[v,k] for k in range(N)) * (scenario.costOffshore + modV) for v in range(vI)) ,# +
        gp.quicksum(gp.quicksum(xPortOpD[v,k] for k in range(N)) * (scenario.costPortOp + modV) for v in range(vI)) +
        gp.quicksum(gp.quicksum(xToSite[v,k] for k in range(N)) * (scenario.costFuel * dur_Movement + modV) for v in range(vI)) +
        gp.quicksum(gp.quicksum(xToPort[v,k] for k in range(N)) * (scenario.costFuel * dur_Movement + modV)  for v in range(vI)) +
        (gp.quicksum(xPortCapacity[k] for k in range(N)) / (N * scenario.maximumPortCapacity)) * scenario.storagePenalty -
        gp.quicksum(xOWT[v, k] * benefit for k in range(N) for v in range(vI)) -
        gp.quicksum( (N - xOWT_TimeFinished[v,k])      / N for v in range(vI) for k in range(N) ) * benefitEarly  -
        gp.quicksum( (N - xMinorOps_TimeFinished[v,k]) / N for v in range(vI) for k in range(N) ) * ((benefitEarly * 0.2) / N / 84) +
        gp.quicksum(gp.quicksum(xPortOpD[v,k] for k in range(N)) for v in range(vI)) * 0.01,
        GRB.MINIMIZE)

    # Constraints
    for v in range(vI):
        for k in range(1, N):
            model.addConstr(capacity[v, k] == capacity[v, k-1] - xOWT[v, k] + xPortOp[v, k])
            model.addConstr(capacity[v, k] <= scenario.maxShipCapacities[v])

    for v in range(vI):
        for k in range(N):
            model.addConstr(xOWT[v, k] + xToPort[v, k] + xToSite[v, k] + xPortOp[v, k] + xBusy[v, k] <= 1)

    # Build times constraints
    for v in range(vI):
        for k in range(N):
            model.addConstr(xOWT_TimeFinished[v, k] == xOWT[v, k] * (k + expectedDuration[0, k] - 1))
            model.addConstr(xMinorOps_TimeFinished[v, k] == (xPortOp[v, k] * (k + expectedDuration[3, k] - 1) +
                                                            xToPort[v, k] * (k + expectedDuration[2, k] - 1) +
                                                            xToSite[v, k] * (k + expectedDuration[1, k] - 1)))

    # Location constraints
    
        
    for v in range(vI):
        for k in range(N):
            if k > 0:
                model.addConstr(location[v, k] == location[v, k-1] - (xToPort[v, k]) + xToSite[v, k])
            else:
                if vI > 1:
                    loc = scenario.currentLocation[v, k] 
                else:
                    loc = scenario.currentLocation[k] 
                model.addConstr(location[v, k] == loc - (xToPort[v, k]) + xToSite[v, k])
            model.addConstr(location[v, k] >= xOWT[v, k])
            model.addConstr(location[v, k] <= (1 - xPortOp[v, k]))

    # Max OWTs to build constraint
    model.addConstr(sum(sum(xOWT[i, j] for j in range(N)) for i in range(vI)) <= scenario.OWTsToBuild - scenario.BuiltOWTs)

    # Duration constraints
    for v in range(vI):
        for k in range(N):
            t_owt = expectedDuration[0, k] - 1
            t_move = expectedDuration[1, k] - 1
            t_port = expectedDuration[3, k] - 1

            k2_owt = np.arange(k + 1, min(k + t_owt + 1, N))
            k2_move = np.arange(k + 1, min(k + t_move + 1, N))
            k2_port = np.arange(k + 1, min(k + t_port + 1, N))
            k2_portD = np.arange(k, min(k + t_port + 1, N))

            model.addConstr(np.sum(xBusy[v, k2_owt]) >= xOWT[v, k] * t_owt)
            model.addConstr(np.sum(xBusy[v, k2_move]) >= (xToPort[v, k] * t_move) + (xToSite[v, k] * t_move))
            model.addConstr(np.sum(xBusy[v, k2_port]) >= xPortOp[v, k] * t_port)
            model.addConstr(np.sum(xPortOpD[v, k2_portD]) >= xPortOp[v, k] * (t_port + 1))

    # Vessel start times constraints
    for v in range(vI):
        for k in range(N):
            if k - scenario.vesselStart[v] + scenario.currentDate <= 0:
                model.addConstr(xOWT[v, k] + xToPort[v, k] + xToSite[v, k] + xPortOp[v, k] + xBusy[v, k] == 0)

    # Loading Bays constraint
    for k in range(N):
        model.addConstr(sum(xPortOpD[i, k] for i in range(vI)) + scenario.blockedBays[0, k] <= scenario.numLoadingBaysInPort)

    # Port Capacity constraints
    for k in range(1, N):
        model.addConstr(xPortCapacity[0, k] == xPortCapacity[0, k-1] - sum(xPortOp[i, k] for i in range(vI)) +
                        (xPortRestockOp[0, k] * scenario.portRestockAmount) - scenario.scheduledLoadingOps[0, k])

    for k in range(0, N, scenario.portRestockFrequency):
        i_sBlock = max(k - scenario.portRestockFrequency, 0)
        model.addConstr(sum(xPortRestockOp[0, i] for i in range(i_sBlock, k)) <= 1)

    if scenario.portRestockEarliest > 1:
        block = min(scenario.portRestockEarliest, N)
        model.addConstr(sum(xPortRestockOp[0, i] for i in range(block)) == 0)

    # Set GUROBI parameters
    model.setParam('TimeLimit', scenario.maxOptimTime)
    model.setParam('OutputFlag', 1)  # Set to 1 to print optimization progress
    
    # Use GUROBI for optimization
    model.optimize()

    # Process the result
    if model.status == GRB.OPTIMAL:
        solution = {
            "location": np.array([[location[v, k].X for k in range(N)] for v in range(vI)]),
            "capacity": np.array([[capacity[v, k].X for k in range(N)] for v in range(vI)]),
            "xOWT": np.array([[xOWT[v, k].X for k in range(N)] for v in range(vI)]),
            "xPortOp": np.array([[xPortOp[v, k].X for k in range(N)] for v in range(vI)]),
            "xToPort": np.array([[xToPort[v, k].X for k in range(N)] for v in range(vI)]),
            "xToSite": np.array([[xToSite[v, k].X for k in range(N)] for v in range(vI)]),
            "xBusy": np.array([[xBusy[v, k].X for k in range(N)] for v in range(vI)]),
            "xPortOpD": np.array([[xPortOpD[v, k].X for k in range(N)] for v in range(vI)]),
            "xOWT_TimeFinished": np.array([[xOWT_TimeFinished[v, k].X for k in range(N)] for v in range(vI)]),
            "xMinorOps_TimeFinished": np.array([[xMinorOps_TimeFinished[v, k].X for k in range(N)] for v in range(vI)]),
            "xPortRestockOp": np.array([[xPortRestockOp[v, k].X for k in range(N)] for v in range(vI)]),
            "xPortCapacity": np.array([[xPortCapacity[v, k].X for k in range(N)] for v in range(vI)]),
            "cost": cost.X
        }
        exitflag = True
    else:
        solution = None
        exitflag = False

    return solution, exitflag
