import matplotlib.pyplot as plt
import numpy as np
from collections import deque

def round_robin_scheduler(processes, quantum):
    # Deep copy to avoid modifying original list
    processes = [p.copy() for p in processes]
    
    # Sort processes by arrival time and then by ID
    processes.sort(key=lambda x: (x['arrival_time'], x['id']))
    
    # Initialize variables
    current_time = 0
    ready_queue = deque()
    completed_processes = []
    total_processes = len(processes)
    cycle_count = 0
    active_processes = 0
    
    # Initialize additional fields for each process
    for process in processes:
        process['remaining_time'] = process['burst_time']
        process['execution_history'] = []
        process['first_executed'] = False
        process['cycle_executed'] = False
        process['in_queue'] = False
    
    print(f"\nTotal number of processes: {total_processes}")
    print("Process order by arrival time:")
    for p in processes:
        print(f"P{p['id']}: Arrival Time = {p['arrival_time']}, Burst Time = {p['burst_time']}")
    
    while processes or ready_queue:
        # Print current state and cycle information
        print(f"\n--- Current Time: {current_time} | Cycle: {cycle_count} ---")
        print("Remaining Processes:", [f"P{p['id']}" for p in processes])
        print("Ready Queue:", [f"P{p['id']}" for p in ready_queue])
        
        # Add newly arrived processes to the ready queue
        while processes and processes[0]['arrival_time'] <= current_time:
            process = processes.pop(0)
            process['in_queue'] = True
            ready_queue.append(process)
            active_processes += 1
            print(f"Added P{process['id']} to ready queue at time {current_time}")
        
        if not ready_queue:
            current_time = processes[0]['arrival_time'] if processes else current_time + 1
            continue
        
        # Check if all active processes in current cycle have executed
        executed_count = sum(1 for p in ready_queue if p['cycle_executed'])
        if executed_count == len(ready_queue) and ready_queue:
            cycle_count += 1
            print(f"\nStarting new cycle {cycle_count} - All processes in queue have executed")
            # Convert ready_queue to list, sort it, and convert back to deque
            ready_queue_list = list(ready_queue)
            ready_queue_list.sort(key=lambda x: (x['arrival_time'], x['id']))
            ready_queue.clear()
            ready_queue.extend(ready_queue_list)
            for p in ready_queue:
                p['cycle_executed'] = False
        
        # Execute processes in order
        if ready_queue:
            # Get the first non-executed process from the queue
            current_process = None
            rotations = 0
            while rotations < len(ready_queue):
                if not ready_queue[0]['cycle_executed']:
                    current_process = ready_queue.popleft()
                    break
                ready_queue.rotate(-1)
                rotations += 1
            
            if current_process is None:
                current_time += 1
                continue
                
            print(f"\nExecuting P{current_process['id']}")
            
            # Execute for quantum time or remaining time, whichever is smaller
            execution_time = min(quantum, current_process['remaining_time'])
            
            # Record execution
            start_time = current_time
            current_time += execution_time
            current_process['remaining_time'] -= execution_time
            current_process['execution_history'].append((start_time, current_time))
            current_process['cycle_executed'] = True
            
            print(f"P{current_process['id']} executed for {execution_time} time units")
            print(f"Remaining time for P{current_process['id']}: {current_process['remaining_time']}")
            
            # Add newly arrived processes before re-queuing the current process
            while processes and processes[0]['arrival_time'] <= current_time:
                process = processes.pop(0)
                ready_queue.append(process)
                print(f"Added P{process['id']} to ready queue at time {current_time}")
            
            # If process is not complete, add it back to the end of the queue
            if current_process['remaining_time'] > 0:
                ready_queue.append(current_process)
                print(f"P{current_process['id']} added back to ready queue at the end")
            else:
                # Process completed
                current_process['execution_time'] = (current_time - current_process['burst_time'] )
                current_process['completion_time'] = current_time
                current_process['turnaround_time'] = current_time - current_process['arrival_time']
                current_process['waiting_time'] = current_process['turnaround_time'] - current_process['burst_time']
                completed_processes.append(current_process)
                active_processes -= 1
                print(f"P{current_process['id']} completed")
    
    # Sort completed processes by ID
    completed_processes.sort(key=lambda x: x['id'])
    
    # Print detailed results
    print("\nROUND ROBIN SIMULATION RESULTS")
    print("-" * 80)
    print("Process | T. Llegada | Rafagas | T. Salida | T.sistema | T. Espera | T. Ejecucion |")
    print("-" * 80)
    
    total_turnaround = 0
    total_waiting = 0
    
    for process in completed_processes:
        print(f"P{process['id']:6} | {process['arrival_time']:10} | {process['burst_time']:7} | {process['completion_time']:9} | {process['turnaround_time']:9} | {process['waiting_time']:9} | {process['execution_time']:12} |")
        total_turnaround += process['turnaround_time']
        total_waiting += process['waiting_time']
    
    print("-" * 80)
    print(f"Tiempo Promedio del Sistema: {total_turnaround/len(completed_processes):.2f}")
    print(f"Tiempo Promedio de Espera: {total_waiting/len(completed_processes):.2f}")
    print(f"GRUPO 1 ALGORITMO ROUND ROBIN")
    
    # Visualize Gantt Chart
    visualize_gantt_chart(completed_processes)
    
    return completed_processes

def visualize_gantt_chart(processes):
    plt.figure(figsize=(15, 8))
    plt.title('Diagrama de Gantt - Round Robin', pad=20, fontsize=14)
    plt.xlabel('Tiempo', fontsize=12)
    plt.ylabel('Procesos', fontsize=12)
    
    # Colores para los procesos
    colors = plt.cm.Set3(np.linspace(0, 1, len(processes)))
    
    # Encontrar el tiempo máximo para el eje x
    max_time = max(end for p in processes for start, end in p['execution_history'])
    
    # Dibujar períodos de ejecución y espera
    for i, process in enumerate(processes):
        # Ordenar los períodos de ejecución
        execution_periods = sorted(process['execution_history'], key=lambda x: x[0])
        
        # Dibujar períodos de espera
        if len(execution_periods) > 0:
            wait_start = process['arrival_time']
            for start, end in execution_periods:
                if wait_start < start:
                    plt.barh(f'P{process["id"]}', start - wait_start, 
                            left=wait_start, color='lightgray', 
                            edgecolor='gray', hatch='//', alpha=0.3)
                wait_start = end
        
        # Dibujar períodos de ejecución
        for start, end in execution_periods:
            duration = end - start
            plt.barh(f'P{process["id"]}', duration, left=start,
                     color=colors[i], edgecolor='black', alpha=0.7)
            # Añadir etiquetas de tiempo
            if duration >= 2:  # Solo mostrar etiqueta si hay suficiente espacio
                plt.text(start + duration/2, f'P{process["id"]}',
                         f'{duration}', ha='center', va='center',
                         fontweight='bold', fontsize=10)
    
    # Ajustar el eje x para mostrar todos los tiempos
    plt.xlim(-0.5, max_time + 0.5)
    
    # Añadir líneas de cuadrícula y leyenda
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    
    # Crear leyenda personalizada
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=colors[0], edgecolor='black', alpha=0.7, label='Ejecución'),
        Patch(facecolor='lightgray', edgecolor='gray', hatch='//', alpha=0.3, label='Espera')
    ]
    plt.legend(handles=legend_elements, loc='upper right')
    
    plt.tight_layout()
    plt.show()

# Función principal para ejecutar
def main():
    procesos = []
    print("\nBienvenido al Simulador de Round Robin")
    print("-" * 40)
    
    # Get quantum time
    quantum = int(input("\nIngrese el quantum de tiempo: "))
    
    # Get number of processes
    n = int(input("Ingrese el número de procesos: "))
    
    # Input process details
    for i in range(n):
        print(f"\nProceso {i+1}:")
        proceso = {
            'id': i + 1,
            'arrival_time': int(input(f"Tiempo de llegada para P{i+1}: ")),
            'burst_time': int(input(f"Tiempo de ejecución para P{i+1}: "))
        }
        procesos.append(proceso)
    
    # Execute scheduler
    round_robin_scheduler(procesos, quantum)

# Ejecutar el script
if __name__ == "__main__":
    main()